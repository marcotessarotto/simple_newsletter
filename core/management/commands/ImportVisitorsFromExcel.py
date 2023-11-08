from django.core.management import BaseCommand
import openpyxl

from core.models import Visitor

def import_excel_to_django_model(excel_file_path):
    # Load the workbook and select the first worksheet
    wb = openpyxl.load_workbook(excel_file_path)
    ws = wb.active

    # Iterate through each row in the worksheet and fetch values
    for row in ws.iter_rows(min_row=2, values_only=True):  # Assuming row 1 is the header
        visitor, created = Visitor.objects.get_or_create(
            id=row[0],
            defaults={
                'company_name': row[2],
                'last_name': row[5],
                'first_name': row[6],
                'job_position': row[7],
                'nationality': row[12],
                'mobile_phone': row[13],
                'email_address': row[14],
            }
        )
        if created:
            print(f'Created Visitor: {visitor.first_name} {visitor.last_name}')
        else:
            print(f'Visitor with ID {visitor.id} already exists.')


class Command(BaseCommand):
    """Import visitors from excel file
    """
    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **options):

        # get file name from command line
        file_path = options["file_path"]
        print(file_path)

        # Call the function with the path to your Excel file
        import_excel_to_django_model(file_path)


