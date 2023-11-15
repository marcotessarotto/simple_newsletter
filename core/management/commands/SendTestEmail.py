from django.core.mail import EmailMessage
from django.core.management import BaseCommand
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class Command(BaseCommand):
    """Send a special email to all visitors.
    The email will link to a short questionnaire to gather information and
    to sign up for the newsletter.
    """
    def add_arguments(self, parser):
        parser.add_argument("email", type=str)
        parser.add_argument("from_email", type=str)

    def handle(self, *args, **options):
        email_address = options["email"]
        from_email = options["from_email"]

        # Define the subject and the HTML content for the email
        subject = "Join Our Newsletter and Questionnaire"
        html_content = render_to_string('email_template.html', {'context': 'values'})
        text_content = strip_tags(html_content)  # Create a plain-text version of the HTML email

        # Create the email message
        email = EmailMessage(
            subject,
            html_content,
            from_email,  # Replace with your sender email
            [email_address]
        )
        email.content_subtype = "html"  # Indicate that the email content is HTML
        email.send()

        self.stdout.write(self.style.SUCCESS(f"Email sent successfully to {email_address}"))
