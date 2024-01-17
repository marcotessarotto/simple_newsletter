from django.core.management import BaseCommand
from datetime import timedelta

from core.models import MessageLog


class Command(BaseCommand):
    """Process message logs."""

    def add_arguments(self, parser):
        pass

    # Function to check if two logs are "near" enough to be in the same group
    @staticmethod
    def is_very_near(log1: MessageLog, log2: MessageLog):
        timedelta_limit = timedelta(milliseconds=100)

        # compare http_real_ip field of log1 and log2
        if log1.http_real_ip == log2.http_real_ip:
            timedelta_limit = timedelta(seconds=2)

        return abs(log1.created_at - log2.created_at) <= timedelta_limit

    # Function to calculate difference in milliseconds
    @staticmethod
    def difference_in_milliseconds(log1, log2):
        return int((log1.created_at - log2.created_at).total_seconds() * 1000)

    def handle(self, *args, **options):
        # Fetch MessageLog instances, ordered by id
        message_logs = MessageLog.objects.filter(processed=False).order_by('id')

        last_id = None
        group_start_instance = None

        for message_log_instance in message_logs:
            if group_start_instance is None:
                group_start_instance = message_log_instance
                group_start_instance.processed = True
                group_start_instance.group_start_id = group_start_instance.id
                group_start_instance.save()
                continue

            print(f"message_log: {message_log_instance.id}")
            print(f"delta: {Command.difference_in_milliseconds(message_log_instance, group_start_instance)} ")

            if Command.is_very_near(group_start_instance, message_log_instance):
                # message_log is in the same group as group_start_instance
                message_log_instance.group_start_id = group_start_instance.id
                message_log_instance.processed = True
                message_log_instance.save()
            else:
                # message_log is in a different group than group_start_instance
                group_start_instance = message_log_instance
                group_start_instance.processed = True
                group_start_instance.group_start_id = group_start_instance.id
                group_start_instance.save()


