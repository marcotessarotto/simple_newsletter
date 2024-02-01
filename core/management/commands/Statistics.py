import time

from django.core.management import BaseCommand
from django.utils import timezone

from core.business_logic import has_message_been_sent_to_subscriber, create_event_log, register_message_delivery
from core.html_utils import make_urls_absolute
from core.models import EmailTemplate, Newsletter, Message, SubscriptionToNewsletter, MessageLog
from core.tasks import send_custom_email_task
from core.template_utils import render_template_from_string
from core.views import generate_unsubscribe_link, generate_message_web_view
from simple_newsletter.settings import NOTIFICATION_BCC_RECIPIENTS, BASE_URL


class Command(BaseCommand):
    """Send newsletter email to all subscribers.
    """

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        # Query to find out how many different 'group_start_id' values are there
        unique_group_start_id_count = MessageLog.objects.values('group_start_id').distinct().count()

        print("Statistics:")
        print("estimation of the number of reads of the newsletter:")
        print(f"There are {unique_group_start_id_count} different Group Start IDs.")





