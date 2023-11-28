from django.core.management import BaseCommand

from core.business_logic import has_message_been_sent_to_subscriber, create_event_log, register_message_delivery
from core.models import EmailTemplate, Newsletter, Message, SubscriptionToNewsletter
from core.tasks import send_custom_email_task
from core.template_utils import render_template_from_string
from core.views import generate_unsubscribe_link, generate_message_web_view
from simple_newsletter.settings import NOTIFICATION_BCC_RECIPIENTS, BASE_URL


class Command(BaseCommand):
    """Send newsletter email to all subscribers.
    """

    def add_arguments(self, parser):
        parser.add_argument("--newsletter", type=str, default=None, required=True, help="Newsletter short name")
        parser.add_argument("--template", type=str, default=None, required=True, help="Template name")
        parser.add_argument("--message", type=int, default=None, required=True, help="Message instance id")

        # add an option called "--nosave" to avoid saving the results to the database
        parser.add_argument("--nosave", action="store_true", default=False, help="Do not save the results to the database")

    def handle(self, *args, **options):

        newsletter = options.get("newsletter")  # newsletter short name
        template = options.get("template")  # template name
        message = options.get("message")  # message instance id

        nosave = options.get("nosave")  # do not save the results to the database

        # print(newsletter)
        # print(template)
        # print(message)

        instance = EmailTemplate.objects.get(name=template)
        template_content = instance.body

        newsletter_instance = Newsletter.objects.get(short_name=newsletter)

        message_instance = Message.objects.get(id=message)

        print(f"newsletter: {newsletter_instance}")
        print(f"message: {message_instance}")

        # get all subscribers:
        rs = SubscriptionToNewsletter.objects.filter(newsletter=newsletter_instance).filter(email__isnull=False) \
            .filter(subscription_confirmed=True).filter(subscribed=True)

        print(f"Subscribers: {rs.count()}")

        # for each subscriber, send an email with a link to the questionnaire
        for subscriber in rs:
            # print(subscriber.email)

            if has_message_been_sent_to_subscriber(subscriber.email, message_instance.id):
                print(f"Message already sent to {subscriber.email}")
                continue
            else:
                print(f"Message not yet sent to {subscriber.email}")

            # each subscriber has a unique token
            context = {
                "subscriber": subscriber,
                # "newsletter": newsletter_instance,
                "message": message_instance,
                "subject": message_instance.subject,
                "content": message_instance.message_content,
                "unsubscribe_link": BASE_URL + generate_unsubscribe_link(subscriber),
                "web_version_view": BASE_URL + generate_message_web_view(message_instance),
            }

            html_content = render_template_from_string(template_content, context=context)

            sender_address = f"{newsletter_instance.name} <{newsletter_instance.from_email}>" if newsletter_instance.name else newsletter_instance.from_email

            send_custom_email_task.delay(
                sender_address,
                subscriber.email,
                message_instance.subject,
                html_content,
                bcc=NOTIFICATION_BCC_RECIPIENTS
            )

            create_event_log(
                event_type="EMAIL_SENT",
                event_title=f"Newsletter email sent to subscriber - message id: {message_instance.id} -  subject: {message_instance.subject}",
                event_data=f"subscriber: {subscriber.email} - template: {template}",
                event_target=subscriber.email
            )

            print(f"Message sent to {subscriber.email}")

            if not nosave:
                register_message_delivery(message_instance.id, subscriber.id)
