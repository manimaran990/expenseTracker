from .models import Category, CategoryGroup

GROUPED_CATEGORIES = {
    'Transit': ['Gas/fuel', 'Taxi', 'Car', 'Parking'],
    'Refund': ['Refund'],
    'Shopping': ['Online Shopping', 'Household supplies', 'Groceries'],
    'Food': ['Fruits', 'Fish/Meat', 'Dining out', 'Restaurant'],
    'Income': ['Paycheck'],
    'Utility': ['Trash', 'TV/Phone/Internet', 'Rent'],
    'Entertainment': ['Entertainment - Other', 'Movies', 'Entertainment'],
    'Insurance': ['Insurance'],
    'Gifts': ['Gifts', 'Cake'],
    'Liquor': ['Liquor'],
    'General': ['General'],
    'Public Transport': ['Bus/train'],
}

for group_name, category_names in GROUPED_CATEGORIES.items():
    group, _ = CategoryGroup.objects.get_or_create(name=group_name)
    for category_name in category_names:
        Category.objects.get_or_create(name=category_name, group=group)