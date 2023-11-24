from django.core.mail import EmailMessage
from django.core.management import BaseCommand
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from core.models import EmailTemplate
from core.tasks import send_custom_email_task
from core.template_utils import render_template_from_string


class Command(BaseCommand):
    """Send a special email to all visitors.
    The email will link to a short questionnaire to gather information and
    to sign up for the newsletter.
    """

    def add_arguments(self, parser):
        parser.add_argument("target_email", type=str)
        parser.add_argument("sender_email", type=str)
        # Adding the optional 'template' argument
        parser.add_argument("--template", type=str, nargs='?', default=None)

        # parser.add_argument("--subject", type=str, nargs='?', default=None)

        # add optional argument

    def handle(self, *args, **options):
        target_email = options["target_email"]
        sender_email = options["sender_email"]
        template = options.get("template")
        # subject = options.get("subject")

        if template:
            instance = EmailTemplate.objects.get(name=template)
            subject = instance.subject
            template_content = instance.body
        else:
            template_content = None

        if not template_content:
            subject = "Join Our Newsletter and Questionnaire"
            html_content = render_to_string('test_email_template.html', {'context': 'values'})
            # text_content = strip_tags(html_content)  # Create a plain-text version of the HTML email
        else:
            html_content = render_template_from_string(template_content, context={})

        send_custom_email_task.delay(
            sender_email,
            target_email,
            subject,
            html_content,
            # bcc=['']
        )

        # # Create the email message
        # email = EmailMessage(
        #     subject,
        #     html_content,
        #     sender_email,  # Replace with your sender email
        #     [target_email_address]
        # )
        # email.content_subtype = "html"  # Indicate that the email content is HTML
        # email.send()

        self.stdout.write(self.style.SUCCESS(f"Email sent successfully to {target_email}"))
