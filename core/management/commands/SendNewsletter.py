from django.core.management import BaseCommand
from django.utils import timezone

from core.business_logic import has_message_been_sent_to_subscriber, create_event_log, register_message_delivery
from core.html_utils import make_urls_absolute
from core.models import EmailTemplate, Newsletter, Message, SubscriptionToNewsletter
from core.tasks import send_custom_email_task
from core.template_utils import render_template_from_string
from core.views import generate_unsubscribe_link, generate_message_web_view
from simple_newsletter.settings import NOTIFICATION_BCC_RECIPIENTS, BASE_URL


class Command(BaseCommand):
    """Send newsletter email to all subscribers.
    """

    def add_arguments(self, parser):
        # parser.add_argument("--newsletter", type=str, default=None, required=True, help="Newsletter short name")
        # parser.add_argument("--template", type=str, default=None, required=True, help="Template name")
        parser.add_argument("--message", type=int, default=None, required=True, help="Message instance id")

        # add an option called "--nosave" to avoid saving the results to the database
        parser.add_argument("--nosave", action="store_true", default=False, help="Do not save the results to the database")
        parser.add_argument("--oksend", action="store_true", default=True, help="send the emails (if true), do not send email if false")

    def handle(self, *args, **options):

        newsletter = options.get("newsletter")  # newsletter short name
        # template = options.get("template")  # template name
        message = options.get("message")  # message instance id

        nosave = options.get("nosave")  # do not save the results to the database
        oksend = options.get("oksend")  # do not send the emails

        # print(newsletter)
        # print(template)
        # print(message)

        message_instance = Message.objects.get(id=message)

        newsletter_instance = message_instance.newsletter
        if not newsletter_instance:
            print("Error: no newsletter instance found")
            return

        # newsletter_instance = Newsletter.objects.get(short_name=newsletter)

        # instance = EmailTemplate.objects.get(name=template)
        template_instance = newsletter_instance.template

        if not template_instance:
            print("Error: no template instance found")
            return

        template_content = template_instance.body

        print(f"message: {message_instance}")
        print(f"newsletter: {newsletter_instance}")
        print(f"template: {template_instance}")

        # get all subscribers of the newsletter that have confirmed their subscription:
        rs = (SubscriptionToNewsletter.objects
              .filter(newsletter=newsletter_instance)
              .filter(email__isnull=False)
              .filter(subscription_confirmed=True)
              .filter(subscribed=True))

        print(f"Subscribers: {rs.count()}")

        counter = 0

        sender_address = f"{newsletter_instance.name} <{newsletter_instance.from_email}>" if newsletter_instance.name else newsletter_instance.from_email
        # check if the sender address is valid

        # for each subscriber, send an email with a link to the questionnaire
        for subscriber in rs:
            # print(subscriber.email)

            if has_message_been_sent_to_subscriber(subscriber.email, message_instance.id):
                print(f"Message already sent to {subscriber.email}, skipping")
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

            html_content = make_urls_absolute(html_content, newsletter_instance.base_url)

            if oksend:
                send_custom_email_task.delay(
                    sender_address,
                    subscriber.email,
                    message_instance.subject,
                    html_content,
                    bcc=NOTIFICATION_BCC_RECIPIENTS,
                    email_settings_id=newsletter_instance.email_settings.id if newsletter_instance.email_settings else None
                )

                create_event_log(
                    event_type="EMAIL_SENT",
                    event_title=f"Newsletter email sent to subscriber - newsletter {newsletter_instance.short_name} message id: {message_instance.id} -  subject: {message_instance.subject}",
                    event_data=f"subscriber: {subscriber.email} - template: {template_instance}",
                    event_target=subscriber.email
                )

                print(f"Message sent to {subscriber.email}")

            if not nosave:
                register_message_delivery(message_instance.id, subscriber.id)

            counter += 1
            if counter >= 1:
                break

        print(f"Sent {counter} messages")

        if not nosave:
            message_instance.processed = True
            message_instance.processed_at = timezone.now()
            message_instance.save()
