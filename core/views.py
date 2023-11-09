from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import SubscriptionForm, VisitSurveyForm
from .models import Newsletter, SubscriptionToNewsletter, Visitor


def subscribe(request, short_name):
    newsletter: Newsletter = get_object_or_404(Newsletter, short_name=short_name)

    if not newsletter.allows_subscription:
        return render(request, 'subscriptions/newsletter_subscription_closed.html')

    if request.method == 'POST':
        form = SubscriptionForm(request.POST)

        print(form)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.ip_address = get_client_ip(request)
            subscription.newsletter = newsletter
            subscription.save()
            # You can add code here to send a confirmation email
            return render(request, 'subscriptions/confirmation.html')
        else:
            print("form is not valid")

    context = {
        'short_name': short_name,
        'form': SubscriptionForm(initial={'newsletter': newsletter}),

    }

    return render(request, 'subscriptions/subscribe.html', context=context)


def generate_unsubscribe_link(subscriber):
    # Use Django's reverse to create the URL for the unsubscribe view
    # Replace 'unsubscribe' with the name of your actual unsubscribe view
    from django.urls import reverse
    return reverse('unsubscribe', args=[str(subscriber.unsubscribe_token)])


def unsubscribe(request, token):
    subscriber = get_object_or_404(SubscriptionToNewsletter, unsubscribe_token=token)

    if request.method != 'POST':
        return render(request, 'subscriptions/unsubscribe.html', {'subscriber': subscriber})

    # Handle the unsubscription process, e.g., mark the subscriber as unsubscribed
    subscriber.subscribed = False
    subscriber.unsubscribed_at = timezone.now()
    subscriber.save()

    # subscriber.delete()  # Or update a 'subscribed' field to False
    return HttpResponse("You have successfully unsubscribed.")



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def visit_survey_newsletter_subscription(request, token):

    visitor: Visitor = get_object_or_404(Visitor, subscribe_token=token)

    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.ip_address = get_client_ip(request)
            subscription.newsletter = newsletter
            subscription.save()
            # You can add code here to send a confirmation email
            return render(request, 'subscriptions/confirmation.html')
        else:
            print("form is not valid")
    else:
        # Map the fields from Visitor to the corresponding fields in SubscriptionForm
        initial_data = {
            'email': visitor.email_address,
            'name': visitor.first_name,
            'surname': visitor.last_name,
            'nationality': visitor.nationality,
            'company': visitor.company_name,
            'role': visitor.job_position,
            'telephone': visitor.mobile_phone,
        }
        form = SubscriptionForm(initial=initial_data)

        survey_form = VisitSurveyForm()

    context = {
        'form': form,
        'survey_form': survey_form,
        'short_name': 'BSBF Trieste 2024',
        'visitor': visitor,
    }


    return render(request, 'subscriptions/visit_survey_newsletter_subscription.html', context=context)
