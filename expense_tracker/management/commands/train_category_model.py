# expense_tracker/management/commands/process_csv.py

from django.core.management.base import BaseCommand, CommandError
from expense_tracker.categorizer import train_model

class Command(BaseCommand):
    help = 'Train labeled dataset for categorizer'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        try:
            train_model(csv_file)

            self.stdout.write(self.style.SUCCESS('Successfully trained model "%s"' % csv_file))
        except Exception as e:
            raise CommandError('Error while processing file: "%s"' % e)
