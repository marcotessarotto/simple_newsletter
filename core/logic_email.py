from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone

from core.models import Message


def send_message(msg: Message):
    if not msg.sent:
        # Construct the email
        email = EmailMessage(
            subject=msg.subject,
            body=msg.content2,  # Using content2 (RichTextUploadingField) as it may contain images
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
