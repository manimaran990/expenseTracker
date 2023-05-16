# expense_tracker/management/commands/process_csv.py

from django.core.management.base import BaseCommand, CommandError
from expense_tracker.bank_statement_loader import CIBC_handler

class Command(BaseCommand):
    help = 'Processes a CSV file using the CIBC handler'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        try:
            handler = CIBC_handler(csv_file)
            handler.get_desc_category()

            self.stdout.write(self.style.SUCCESS('Successfully processed file "%s"' % csv_file))
        except Exception as e:
            raise CommandError('Error while processing file: "%s"' % e)
