from django.core.management import BaseCommand
from django.db.models import F
from datetime import timedelta
import itertools

from core.models import MessageLog


class Command(BaseCommand):
    """Process message logs."""

    def add_arguments(self, parser):
        pass

    # Function to check if two logs are within 10 milliseconds
    def is_very_near(log1, log2):
        return abs(log1.created_at - log2.created_at) <= timedelta(milliseconds=60)

    # Function to calculate difference in milliseconds
    def difference_in_milliseconds(log1, log2):
        return int((log1.created_at - log2.created_at).total_seconds() * 1000)

    def handle(self, *args, **options):
        # Fetch MessageLog instances, ordered by created_at
        message_logs = MessageLog.objects.filter(processed=False).order_by('id')

        last_id = None
        group_start_instance = None

        for message_log in message_logs:
            if group_start_instance is None:
                group_start_instance = message_log
                group_start_instance.processed = True
                group_start_instance.group_start_id = group_start_instance.id
                group_start_instance.save()
                continue

            print(f"message_log: {message_log.id}")
            print(f"delta: {Command.difference_in_milliseconds(message_log, group_start_instance)} ")

            if Command.is_very_near(group_start_instance, message_log):
                # message_log is in the same group as group_start_instance
                message_log.group_start_id = group_start_instance.id
                message_log.processed = True
                message_log.save()
            else:
                # message_log is in a different group than group_start_instance
                group_start_instance = message_log
                group_start_instance.processed = True
                group_start_instance.group_start_id = group_start_instance.id
                group_start_instance.save()


