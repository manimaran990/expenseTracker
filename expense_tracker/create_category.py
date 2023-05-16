from .models import Category, CategoryGroup, GROUPED_CATEGORIES


def create_category_groups():
    for group_name, category_names in GROUPED_CATEGORIES.items():
        group, _ = CategoryGroup.objects.get_or_create(name=group_name)
        for category_name in category_names:
            Category.objects.get_or_create(name=category_name, group=group)