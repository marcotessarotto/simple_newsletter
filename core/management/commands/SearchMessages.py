from django.core.management import BaseCommand
from django.db.models import F
from datetime import timedelta
import itertools

from core.models import MessageLog, Message


class Command(BaseCommand):
    """Process message logs."""

    def add_arguments(self, parser):

        parser.add_argument("search_string", type=str)

    def handle(self, *args, **options):

        search_string = options["search_string"]

        # # Fetch MessageLog instances, ordered by id
        # messages = Message.objects.all().order_by('id')
        #
        # for message in messages:
        #
        #     if search_string in message.message_content:
        #         print(f"search string has been found in message_log: {message.id}")
        #
        # print()

        matching_messages = Message.search_in_message_content(search_string)

        if matching_messages:
            print(f"search string has been found in {len(matching_messages)} messages")
            for message in matching_messages:
                print(message.id)
        else:
            print("search string has not been found in any message")