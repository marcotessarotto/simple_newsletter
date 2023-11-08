from django.core.management import BaseCommand

from core.models import Visitor


class Command(BaseCommand):
    """Send a special email to all visitors.
    The email will link to a short questionnaire to gather information and
    to sign up for the newsletter.
    """
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        # get all Visitors

        rs = Visitor.objects.filter(email_address__isnull=False).filter(email_sent=False)

        # for each visitor, send an email with a link to the questionnaire
        for visitor in rs:

            # subject = 'Welcome to the Digital Culture Lab!'

            # message = f'Dear {visitor.first_name} {visitor.last_name},\n\n' \

            pass