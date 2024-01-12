from django.core.management import BaseCommand
from django.db.models import F
from datetime import timedelta
import itertools

from core.models import MessageLog


class Command(BaseCommand):
    """Process message logs."""

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # Fetch MessageLog instances, ordered by created_at
        message_logs = MessageLog.objects.all().order_by('id')

        for message_log in message_logs:
            # print(f"message_log: {message_log}")
            message_log.processed = False
            message_log.group_start_id = 0
            message_log.save()

