from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from core.logic_email import send_custom_email
from core.models import SubscriptionToNewsletter


@shared_task
def send_custom_email_task(sender_email, recipient_email, subject, html_content, bcc=None):
    return send_custom_email(sender_email, recipient_email, subject, html_content, bcc)


@shared_task
def process_subscription_task(subscription_id):
    subscription: SubscriptionToNewsletter = SubscriptionToNewsletter.objects.get(id=subscription_id)

    if subscription.verification_email_sent:
        # email already sent, do nothing
        return

    context = {
        'newsletter_title': subscription.newsletter.name,
        'confirmation_link': f"{settings.BASE_URL}/confirm-subscription/{subscription.id}/{subscription.subscribe_token}",
        'signature': subscription.newsletter.signature,
        'subscription': subscription,
    }

    # Define the subject and the HTML content for the email
    subject = f"Confirm Your Subscription to {subscription.newsletter.name}"
    html_content = render_to_string('confirm_subscription_template.html', context=context)

    # subject = f"Confirm your subscription to our newsletter {subscription.newsletter.name}"


    # we need to send a verification email

    send_custom_email_task.delay(
        newsletter.from_email,
        subscription.email,
        'Your Subject',
        '<p>Your HTML content here</p>',
        bcc=['bcc@example.com']
    )