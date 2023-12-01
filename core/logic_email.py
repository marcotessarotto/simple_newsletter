from django.core.mail import EmailMessage
from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend
from django.utils import timezone

from core.models import Message, EmailSettings


def send_message(msg: Message):
    if not msg.sent:
        # Construct the email
        email = EmailMessage(
            subject=msg.subject,
            body=msg.message_content,  # Using content2 (RichTextUploadingField) as it may contain images
            from_email=settings.EMAIL_HOST_USER,
            to=[msg.newsletter.from_email],  # Assuming the newsletter model has a from_email attribute to send to
        )
        email.content_subtype = 'html'  # Indicate that the email body is in HTML format

        # Send the email
        email.send()

        # Update the Message model to reflect that it's been sent
        msg.sent = True
        msg.sent_at = timezone.now()  # Don't forget to import timezone from django.utils
        msg.save()
    else:
        print("Message has already been sent.")


def send_custom_email(sender_email, recipient_email, subject, html_content, bcc=None, email_settings_id=None):
    """
    Send a custom HTML email to a given email address, with optional BCC.

    Args:
    sender_email (str): The sender's email address.
    recipient_email (str): The recipient's email address.
    subject (str): The subject of the email.
    html_content (str): The HTML content of the email.
    bcc (list, optional): List of email addresses to BCC.
    """

    email_settings = EmailSettings.objects.get(id=email_settings_id) if email_settings_id else None

    # Setup email backend with settings from the model
    backend = EmailBackend(
        host=email_settings.host,
        port=email_settings.port,
        username=email_settings.username,
        password=email_settings.password,
        use_tls=email_settings.use_tls
    ) if email_settings else None

    print(f"email_settings: {email_settings}")
    print(f"backend: {backend}")

    # Create the email message
    email = EmailMessage(
        subject,
        html_content,
        sender_email,  # Sender's email
        [recipient_email],  # Recipient's email
        bcc=bcc,  # BCC recipients
        connection=backend  # Optional connection backend
    )
    email.content_subtype = "html"  # Indicate that the email content is HTML
    email.send()  # Send the email
