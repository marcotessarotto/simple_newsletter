from django.core.management.base import BaseCommand, CommandError
from core.models import SubscriptionToNewsletter, Newsletter
import pandas as pd
from django.utils.timezone import now


class Command(BaseCommand):
    help = 'Import subscribers from an Excel file and associate them with a specific newsletter.'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='The filename of the Excel file to import')
        parser.add_argument('newsletter_id', type=int,
                            help='The ID of the Newsletter instance to associate with the subscribers')

        # add an optional string argument called "--motivation" to the command
        parser.add_argument("--motivation", type=str, default="import from excel", required=False, help="Motivation for the subscription")

    def handle(self, *args, **options):
        filename = options['filename']
        newsletter_id = options['newsletter_id']

        motivation = options['motivation']

        try:
            # Retrieve the Newsletter instance
            try:
                newsletter_instance = Newsletter.objects.get(id=newsletter_id)
            except Newsletter.DoesNotExist as e:
                raise CommandError(
                    f'Newsletter with id "{newsletter_id}" does not exist'
                ) from e

            # Read the Excel file
            df = pd.read_excel(filename)

            # Iterate over the rows of the DataFrame
            for index, row in df.iterrows():

                subscription_to_newsletter = row['subscription_to_newsletter']

                if not subscription_to_newsletter:
                    print(f"subscription_to_newsletter is False, skipping... email: {row['email']}")
                    continue

                if row['email'] is None:
                    print(f"email is None, skipping... email: {row['email']}")
                    continue

                # check if the email address is already in the database
                if SubscriptionToNewsletter.objects.filter(email__iexact=row['email'].lower()).exists():
                    print(f"Email {row['email']} already exists in the database, skipping...")
                    continue

                honorific = row.get('honorific')

                subscription = SubscriptionToNewsletter(
                    newsletter=newsletter_instance,
                    honorific=honorific if honorific in dict(SubscriptionToNewsletter.HONORIFICS) else "",
                    email=row['email'],
                    name=row.get('name', ''),
                    surname=row.get('surname', ''),
                    nationality=row.get('nationality', ''),
                    company=row.get('company', ''),
                    role=row.get('role', ''),
                    telephone=row.get('telephone', ''),
                    ip_address='127.0.0.1',  # Replace with actual IP if available
                    privacy_policy_accepted=True,
                    notes='Imported from Excel',
                    subscription_source=motivation,
                    subscribed=True,
                    verification_email_sent=False,
                    # verification_email_sent_at=now(),
                    subscription_confirmed=True,
                    # subscription_confirmed_at=now(),
                )
                subscription.save()

                print(f"Created subscription: {subscription}")

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported subscribers from "{filename}" and associated them with newsletter id "{newsletter_id}"'
                )
            )

        except FileNotFoundError:
            raise CommandError(f'File "{filename}" does not exist')
        except Exception as e:
            print(e)
            raise CommandError(f'An error occurred: {e}') from e
