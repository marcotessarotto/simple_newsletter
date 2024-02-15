from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from core.business_logic import create_event_log
from core.logic_email import send_custom_email
from core.models import SubscriptionToNewsletter, MessageLog, Message
from simple_newsletter.settings import NOTIFICATION_BCC_RECIPIENTS


@shared_task
def send_custom_email_task(sender_email, recipient_email, subject, html_content, bcc=None, email_settings_id=None):
    return send_custom_email(sender_email, recipient_email, subject, html_content, bcc, email_settings_id)


@shared_task
def register_static_access_log(log_dict):

    print(f"register_static_access: {log_dict}")

    new_log = MessageLog.create_new_message_log(log_dict)


@shared_task
def register_static_access_log_inc_email_view_counter(log_dict, message_id):

    print(f"register_static_access_log_inc_email_view_counter: {log_dict} message_id={message_id}")

    new_log = MessageLog.create_new_message_log(log_dict)

    if message_instance := Message.objects.get(id=message_id):
        message_instance.increment_email_view_counter()



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
                      bcc=NOTIFICATION_BCC_RECIPIENTS,
                      email_settings_id=newsletter_instance.email_settings.id if newsletter_instance.email_settings else None
                      )

    subscription.verification_email_sent = True
    subscription.verification_email_sent_at = timezone.now()
    subscription.save()

    create_event_log(
        event_type="CONFIRM_SUBSCRIPTION_EMAIL_SENT",
        event_title=f"Confirm subscription email sent to subscriber - newsletter {newsletter_instance.short_name}"
                    f" - subject: {subject}",
        event_data=f"subscriber: {subscription.email}",
        event_target=subscription.email
    )

