from django.core.management.base import BaseCommand, CommandError
from core.models import SubscriptionToNewsletter, Newsletter
import pandas as pd
from django.utils.timezone import now


class Command(BaseCommand):
    help = 'Import subscribers from an Excel file and associate them with a specific newsletter.'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='The filename of the Excel file to import')
        parser.add_argument('newsletter_id', type=int, help='The ID of the Newsletter instance to associate with the subscribers')

    def handle(self, *args, **options):
        filename = options['filename']
        newsletter_id = options['newsletter_id']

        try:
            # Retrieve the Newsletter instance
            try:
                newsletter_instance = Newsletter.objects.get(id=newsletter_id)
            except Newsletter.DoesNotExist:
                raise CommandError(f'Newsletter with id "{newsletter_id}" does not exist')

            # Read the Excel file
            df = pd.read_excel(filename)

            # Iterate over the rows of the DataFrame
            for index, row in df.iterrows():

                # check if the email address is already in the database
                if SubscriptionToNewsletter.objects.filter(email=row['email']).exists():
                    print(f"Email {row['email']} already exists in the database, skipping...")
                    continue


                subscription = SubscriptionToNewsletter(
                    newsletter=newsletter_instance,
                    honorific=row['honorific'] if row['honorific'] in dict(SubscriptionToNewsletter.HONORIFICS) else "",
                    email=row['email'],
                    name=row['name'],
                    surname=row['surname'],
                    nationality=row['nationality'],
                    company=row['company'],
                    role=row['role'],
                    telephone=row['telephone'],
                    ip_address='-',  # Replace with actual IP if available
                    privacy_policy_accepted=True,  # Set according to your data
                    notes='Imported from Excel',
                    subscription_source='import',
                    subscribed=True,
                    verification_email_sent=False,
                    # verification_email_sent_at=now(),
                    subscription_confirmed=True,
                    # subscription_confirmed_at=now(),
                )
                subscription.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported subscribers from "{filename}" and associated them with newsletter id "{newsletter_id}"'
                )
            )

        except FileNotFoundError:
            raise CommandError(f'File "{filename}" does not exist')
        except Exception as e:
            raise CommandError(f'An error occurred: {e}') from e
