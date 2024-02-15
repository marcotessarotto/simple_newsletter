from django.core.management import BaseCommand
from django.db.models import F
from datetime import timedelta
import itertools

from core.models import MessageLog, Message


class Command(BaseCommand):
    """list newsletter messages."""

    def add_arguments(self, parser):
        parser.add_argument("--newsletter_id", type=int, default=None, required=True, help="newsletter id")

        # parser.add_argument("search_string", type=str)

    def handle(self, *args, **options):

        # search_string = options["search_string"]
        newsletter_id = options["newsletter_id"]

        # # Fetch MessageLog instances, ordered by id
        messages = Message.objects.all().order_by('id')

        # Fetch Message instances, ordered by id, filtering by newsletter_id, id descending
        messages = Message.objects.filter(newsletter_id=newsletter_id).order_by('-id')

        for message in messages:
            print(f"message id: {message.id}, message subject: {message.subject}, message content: {message.message_content}")
            print()

        print()
        print(f"Total number of messages: {len(messages)}")
        print()
