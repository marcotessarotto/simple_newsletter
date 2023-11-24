from django.core.management import BaseCommand
from django.utils import timezone

from core.business_logic import create_event_log
from core.models import Visitor, EmailTemplate
from core.template_utils import render_template_from_string
from core.tasks import send_custom_email_task
from simple_newsletter.settings import NOTIFICATION_BCC_RECIPIENTS


class Command(BaseCommand):
    """Send a special email to all visitors.
    The email will link to a short questionnaire to gather information and
    to sign up for the newsletter.
    """
    def add_arguments(self, parser):
        parser.add_argument("sender_email", type=str)
        parser.add_argument("--template", type=str, default=None)

    def handle(self, *args, **options):
        sender_email = options["sender_email"]
        template = options.get("template")

        instance = EmailTemplate.objects.get(name=template)
        subject = instance.subject
        template_content = instance.body

        html_content = render_template_from_string(template_content, context={})
        # get all Visitors

        rs = Visitor.objects.filter(email_address__isnull=False).filter(email_sent=False)

        counter = 0

        # for each visitor, send an email with a link to the questionnaire
        for visitor in rs:
            print(visitor.email_address)

            send_custom_email_task.delay(
                sender_email,
                visitor.email_address,
                subject,
                html_content,
                bcc=NOTIFICATION_BCC_RECIPIENTS
            )

            visitor.email_sent = True
            visitor.email_sent_at = timezone.now()
            visitor.save()

            create_event_log(
                event_type="EMAIL_SENT",
                event_title=f"Email sent to visitor - subject: {subject}",
                event_data=f"Visitor: {visitor.email_address} - template: {template}",
                event_target=visitor.email_address
            )

            counter += 1
            if counter % 5 == 0:
                break

        print(f"Sent {counter} emails")

