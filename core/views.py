from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse

from .business_logic import create_event_log
from .forms import SubscriptionForm, VisitSurveyForm
from .html_utils import make_urls_absolute
from .models import Newsletter, SubscriptionToNewsletter, Visitor, Message
from .tasks import send_custom_email_task, process_subscription_task, register_static_access_log
from .template_utils import render_template_from_string


def home(request):
    return render(request, 'home.html')


def proxy_django_auth(request):
    """used for authentication by nginx when accessing static media files"""
    if request.user.is_authenticated:
        return HttpResponse(status=200)
    return HttpResponse(status=403)


def notify_media_access(request):
    """Used by Nginx for logging when accessing static media files."""

    # request.META: {'wsgi.errors': <gunicorn.http.wsgi.WSGIErrorsWrapper object at 0x7fd0b3122dd0>,
    # 'wsgi.version': (1, 0), 'wsgi.multithread': False, 'wsgi.multiprocess': True, 'wsgi.run_once': False,
    # 'wsgi.file_wrapper': <class 'gunicorn.http.wsgi.FileWrapper'>, 'wsgi.input_terminated': True,
    # 'SERVER_SOFTWARE': 'gunicorn/21.2.0', 'wsgi.input': <gunicorn.http.body.Body object at 0x7fd0b2f58850>,
    # 'gunicorn.socket': <socket.socket fd=9, family=1, type=1, proto=0, laddr=/run/gunicorn-simple-newsletter.sock>,
    # 'REQUEST_METHOD': 'GET', 'QUERY_STRING': '', 'RAW_URI': '/notify_media_access/',
    # 'SERVER_PROTOCOL': 'HTTP/1.0', 'HTTP_HOST': 'newsletter.bsbf2024.org',
    # 'HTTP_X_REAL_IP': '95.214.216.18', 'HTTP_X_FORWARDED_FOR': '95.214.216.18',
    # 'HTTP_X_FORWARDED_PROTO': 'https',
    # 'HTTP_X_ORIGINAL_URI': '/media/content/ckeditor/2023/12/21/fvg_auguri_bsbf_2024_def_small_tBSJcBy.jpg',
    # 'HTTP_CONNECTION': 'close',
    # 'HTTP_USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
    # 'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    # 'HTTP_ACCEPT_LANGUAGE': 'en-US,en;q=0.5',
    # 'HTTP_ACCEPT_ENCODING': 'gzip, deflate, br',
    # 'HTTP_REFERER': 'https://newsletter.bsbf2024.org/view_message/ee9edf9a-73fc-4677-ba76-d01acafd100c/',
    # 'HTTP_COOKIE': 'csrftoken=gE90dl9YCKQdXcEzKLCtGxxHOKes6Eg7; sessionid=xntt5n8al95rcknb5m75mfgmi5154cn4; ckCsrfToken=56hRxCcmnBb66CYE03OSBUucvEm7o4FV8d63T799', 'HTTP_UPGRADE_INSECURE_REQUESTS': '1', 'HTTP_SEC_FETCH_DEST': 'document', 'HTTP_SEC_FETCH_MODE': 'navigate', 'HTTP_SEC_FETCH_SITE': 'same-origin', 'HTTP_SEC_FETCH_USER': '?1', 'HTTP_IF_MODIFIED_SINCE': 'Thu, 21 Dec 2023 15:15:31 GMT', 'HTTP_IF_NONE_MATCH': '"65845693-14efb"', 'wsgi.url_scheme': 'https', 'REMOTE_ADDR': '',
    # 'SERVER_NAME': 'newsletter.bsbf2024.org', 'SERVER_PORT': '443', 'PATH_INFO': '/notify_media_access/', 'SCRIPT_NAME': '', 'CSRF_COOKIE': 'gE90dl9YCKQdXcEzKLCtGxxHOKes6Eg7'}

    if request.META:
        try:

            log_dict = {
                'original_uri': request.META.get('HTTP_X_ORIGINAL_URI', '-'),
                'http_referer': request.META.get('HTTP_REFERER', '-'),
                'http_user_agent': request.META.get('HTTP_USER_AGENT', 'unknown'),
                'http_real_ip': request.META.get('HTTP_X_REAL_IP', 'unknown'),
                'http_cookie': request.META.get('HTTP_COOKIE', '-'),
            }

            print(f"calling register_static_access_log: {log_dict}")
            register_static_access_log.delay(log_dict)

        except Exception as e:
            print(f"notify_media_access - Exception: {e}")
    else:
        print("notify_media_access - no request.META")

    return HttpResponse(status=200)


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

    message.increment_web_view_counter()

    context = {
        'message': message,
        'newsletter_title': message.newsletter.name,
        'subject': message.subject,
        'content': message_content,
        'newsletter_signature': message.newsletter.signature,
    }

    template_for_web_view = message.newsletter.template_for_web_view

    if template_for_web_view:
        template_content = template_for_web_view.body
        html_content = render_template_from_string(template_content, context=context)

        return HttpResponse(html_content)
    else:
        print("no template for web view")

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
    rs = SubscriptionToNewsletter.objects.filter(email=subscriber.email).filter(subscribed=True).filter(
        newsletter=subscriber.newsletter)

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
