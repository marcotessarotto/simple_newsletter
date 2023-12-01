from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse

from .business_logic import create_event_log
from .forms import SubscriptionForm, VisitSurveyForm
from .html_utils import make_urls_absolute
from .models import Newsletter, SubscriptionToNewsletter, Visitor, Message
from .tasks import send_custom_email_task, process_subscription_task


def proxy_django_auth(request):
    """used for authentication by nginx when accessing static media files"""
    if request.user.is_authenticated:
        return HttpResponse(status=200)
    return HttpResponse(status=403)


def confirm_subscription(request, token):
    subscription: SubscriptionToNewsletter = get_object_or_404(SubscriptionToNewsletter, subscribe_token=token)

    context = {
        'newsletter_title': subscription.newsletter.name,
        'signature': subscription.newsletter.signature,
    }

    if subscription.subscription_confirmed:
        return render(request, 'subscriptions/subscription_already_confirmed.html', context=context)

    subscription.subscription_confirmed = True
    subscription.subscription_confirmed_at = timezone.now()
    subscription.save()

    create_event_log(
        event_type="SUBSCRIPTION_CONFIRMED",
        event_title=f"Subscription confirmed by user - newsletter {subscription.newsletter.short_name}",
        event_data=f"Subscription: {subscription.id} - {subscription.email}",
        event_target=subscription.email
    )

    return render(request, 'subscriptions/subscription_confirmed_by_user.html', context=context)


def generate_unsubscribe_link(subscriber):
    # Use Django's reverse to create the URL for the unsubscribe view
    return reverse('unsubscribe', args=[str(subscriber.unsubscribe_token)])


def generate_message_web_view(message):
    return reverse('view_message', args=[str(message.view_token)])


def message_web_view(request, token):
    """This view is used to view the message in the browser, without opening the email client."""
    message = get_object_or_404(Message, view_token=token)

    message_content = make_urls_absolute(message.message_content, message.newsletter.base_url)

    context = {
        'message': message,
        'newsletter_title': message.newsletter.name,
        'subject': message.subject,
        'content': message_content,
        'newsletter_signature': message.newsletter.signature,
    }

    message.increment_web_view_counter()

    return render(request, 'subscriptions/message_web_view.html', context=context)


def unsubscribe(request, token):
    subscriber: SubscriptionToNewsletter = get_object_or_404(SubscriptionToNewsletter, unsubscribe_token=token)

    if not subscriber.subscribed:
        return render(request, 'subscriptions/unsubscribe_previously.html', {'subscriber': subscriber})

    if request.method != 'POST':
        return render(request, 'subscriptions/unsubscribe.html', {'subscriber': subscriber})

    # get browser user agent
    user_agent = request.META.get('HTTP_USER_AGENT') if request.META else "unknown"

    # get request ip address
    ip_address = get_client_ip(request)
    msg = f"unsubscribed web view - ip address: {ip_address} - user_agent: '{user_agent}'"

    # Handle the unsubscription process, e.g., mark the subscriber as unsubscribed
    subscriber.unsubscribe(additional_notes=msg)

    # since at the moment multiple subscriptions with the same email are allowed to the same newsletter,
    # we do a query to check if there are other subscriptions with the same email
    rs = SubscriptionToNewsletter.objects.filter(email=subscriber.email).filter(subscribed=True).filter(newsletter=subscriber.newsletter)

    for s in rs:
        print(f"unsubscribe - {s.id} {s.email} {s.subscribed} {s.newsletter.short_name}")
        s.unsubscribe(additional_notes=msg)

    return render(request, 'subscriptions/unsubscribe_successful.html', {'subscriber': subscriber})


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def survey_newsletter_subscription(request, short_name):
    newsletter: Newsletter = get_object_or_404(Newsletter, short_name=short_name)

    if not newsletter.allows_subscription:
        return render(request, 'subscriptions/newsletter_subscription_closed.html')

    if request.method == 'POST':
        form = SubscriptionForm(request.POST)

        survey_form = VisitSurveyForm(request.POST)

        survey = None

        if survey_form.is_valid():
            survey = survey_form.save(commit=False)
            survey.ip_address = get_client_ip(request)
            # survey.save()

        if form.is_valid():

            # save the survey only if the subscription is valid
            if survey:
                survey.save()

            subscription: SubscriptionToNewsletter = form.save(commit=False)
            subscription.ip_address = get_client_ip(request)
            subscription.newsletter = newsletter

            if subscription.privacy_policy_accepted == '':
                subscription.privacy_policy_accepted = False

            # form['subscribe_to_newsletter'].value() returns a string
            subscribed_to_newsletter = form['subscribe_to_newsletter'].value().lower() == 'true'

            # subscribe_to_newsletter: True, privacy_policy_accepted: True => ok, subscribe to newsnetter
            # subscribe_to_newsletter: True, privacy_policy_accepted: False => error
            # subscribe_to_newsletter: False, privacy_policy_accepted: True => ok
            # subscribe_to_newsletter: False, privacy_policy_accepted: False => ok

            if subscribed_to_newsletter and not subscription.privacy_policy_accepted:
                # should not pass here
                print("error: subscription to newsletter requested but privacy policy not accepted")
            else:
                if subscribed_to_newsletter and subscription.privacy_policy_accepted:
                    print("save subscription to newsletter")
                    subscription.subscription_source = "visit survey"
                    subscription.save()

                    # this step will send a confirmation email
                    process_subscription_task.delay(subscription.id)

                context = {
                    'newsletter_title': newsletter.name,
                    'signature': newsletter.signature,
                    'from_email': newsletter.from_email,
                    'subscription': subscription,
                    'ask_survey': True,
                    'subscribed_to_newsletter': subscribed_to_newsletter,
                }

                return render(request, 'subscriptions/confirmation.html', context=context)

        else:
            print("form is not valid")

    else:
        form = SubscriptionForm(all_fields_required=False)

        survey_form = VisitSurveyForm()

    context = {
        'title': 'Survey and newsletter subscription',
        'form': form,
        'survey_form': survey_form,
        'short_name': newsletter.name,
        'survey_title': newsletter.survey_title,
        'privacy_policy': newsletter.privacy_policy,
        'ask_survey': True,
    }

    return render(request, 'subscriptions/visit_survey_newsletter_subscription.html', context=context)


def subscribe_to_newsletter(request, short_name):
    newsletter: Newsletter = get_object_or_404(Newsletter, short_name=short_name)

    if not newsletter.allows_subscription:
        return render(request, 'subscriptions/newsletter_subscription_closed.html')

    if request.method == 'POST':
        form = SubscriptionForm(request.POST, all_fields_required=True, check_newsletter_subscription=True)

        if form.is_valid():
            subscription: SubscriptionToNewsletter = form.save(commit=False)
            subscription.ip_address = get_client_ip(request)
            subscription.newsletter = newsletter

            if subscription.privacy_policy_accepted == '':
                subscription.privacy_policy_accepted = False

            # form['subscribe_to_newsletter'].value() returns a string
            subscribed_to_newsletter = form['subscribe_to_newsletter'].value().lower() == 'true'

            if not subscribed_to_newsletter and subscription.privacy_policy_accepted:
                raise ValidationError("You should choose 'Yes' to subscribe to the newsletter.")

            if subscription.privacy_policy_accepted and subscribed_to_newsletter:
                subscription.subscription_source = "web form"
                subscription.save()

                # this step will send a confirmation email
                process_subscription_task.delay(subscription.id)

                context = {
                    'newsletter_title': newsletter.name,
                    'signature': newsletter.signature,
                    'from_email': newsletter.from_email,
                    'subscription': subscription,
                    'ask_survey': False,
                    'subscribed_to_newsletter': subscribed_to_newsletter,
                }

                return render(request, 'subscriptions/confirmation.html', context=context)
            else:
                print("privacy policy not accepted")
        else:
            print("form is not valid")

    else:
        form = SubscriptionForm(all_fields_required=True)

    context = {
        'title': 'Newsletter subscription',
        'form': form,
        'short_name': newsletter.name,
        'privacy_policy': newsletter.privacy_policy,
        'ask_survey': False,
    }

    return render(request, 'subscriptions/visit_survey_newsletter_subscription.html', context=context)


