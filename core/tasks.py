from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from core.logic_email import send_custom_email
from core.models import SubscriptionToNewsletter
from simple_newsletter.settings import NOTIFICATION_BCC_RECIPIENTS


@shared_task
def send_custom_email_task(sender_email, recipient_email, subject, html_content, bcc=None):
    return send_custom_email(sender_email, recipient_email, subject, html_content, bcc)


@shared_task
def process_subscription_task(subscription_id):
    subscription: SubscriptionToNewsletter = SubscriptionToNewsletter.objects.get(id=subscription_id)

    if not subscription.privacy_policy_accepted:
        # privacy policy not accepted, do nothing
        print("privacy policy not accepted, do nothing")
        return

    if subscription.verification_email_sent:
        # email already sent, do nothing
        print("verification email already sent, do nothing")
        return

    newsletter_instance = subscription.newsletter

    sender_address = f"{newsletter_instance.name} <{newsletter_instance.from_email}>" if newsletter_instance.name else newsletter_instance.from_email

    context = {
        'newsletter_title': subscription.newsletter.name,
        'confirmation_link': f"{settings.BASE_URL}/confirm-subscription/{subscription.subscribe_token}",
        'signature': subscription.newsletter.signature,
        'subscription': subscription,
    }

    # Define the subject and the HTML content for the email
    subject = f"Confirm your subscription to {subscription.newsletter.name}"
    html_content = render_to_string('confirm_subscription_template.html', context=context)

    send_custom_email(sender_address,
                      subscription.email,
                      subject,
                      html_content,
                      bcc=NOTIFICATION_BCC_RECIPIENTS
                      )

    subscription.verification_email_sent = True
    subscription.verification_email_sent_at = timezone.now()
    subscription.save()
