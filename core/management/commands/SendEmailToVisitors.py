from django.core.management import BaseCommand


class Command(BaseCommand):
    """Send a special email to all visitors.
    The email will link to a short questionnaire to gather information and
    to sign up for the newsletter.
    """
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        pass
