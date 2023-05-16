# expense_tracker/management/commands/process_csv.py

from django.core.management.base import BaseCommand, CommandError
from expense_tracker.create_category import create_category_groups
from expense_tracker.models import Category, CategoryGroup

class Command(BaseCommand):
    help = 'Populate category and category group models'

    # def add_arguments(self, parser):
    #     parser.add_argument('csv_file', type=str, help='The path to the CSV file')

    def handle(self, *args, **options):

        try:
            create_category_groups()

            cat_count = Category.objects.count()
            cat_group_count = CategoryGroup.objects.count()
            self.stdout.write(self.style.SUCCESS(f'Successfully populated category: {cat_count} and catgroups: {cat_group_count}'))

        except Exception as e:
            raise CommandError('Error while populating category and catgroups: "%s"' % e)
