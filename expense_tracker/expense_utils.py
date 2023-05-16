import pickle
from .models import Category, CategoryGroup, GROUPED_CATEGORIES
from collections import namedtuple
import re

model_path = 'expense_tracker/trained_model.pkl'
catgroup = namedtuple('Catgroup', ['group', 'category'])


def clean_description(description):
    description = description.replace("'", "")
    cleaned_string = re.sub(r'\s+', ' ', description)
    return re.sub(r'[^a-zA-Z\s]', '', cleaned_string).strip()

def load_trained_model(model_path):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model
    

model = load_trained_model(model_path)

def regex_mapping(description):
    patterns = {
        'Paycheck': r'\b(infosys)\b',
        'Transfer': r'\b(etransfer|internet banking etransfer|internet transfer|remitly|global money transfer)\b',
        'Payment': r'\b(bill pay|hydroquebec)\b',
        'Service charge': r'\b(service charge)\b',
        'Refund': r'\b(deposit canada|deposit versanti)\b',
        'Withdraw': r'\b(withdrawal|atm)\b',
        'Shopping': r'\b(point of sale|retail purchase|costco)\b',
        'Interest': r'\b(interest)\b'
    }

    for category, pattern in patterns.items():
        if re.search(pattern, description, re.IGNORECASE):
            return category

    return None

def get_cat_group(description, account):
    cleaned_description = re.sub(r'[^a-zA-Z\s]', '', description.lower())
    cleaned_description = cleaned_description.strip()
    if account == 'CIBC - Credit' or account == 'Splitwise':
        predicted_category = model.predict([cleaned_description])[0].strip().capitalize()
    elif account == 'CIBC - Chequing':
        predicted_category = regex_mapping(description)
    else:
        pass

    group_name = None
    category_name = None
     # Iterate through GROUPED_CATEGORIES to find the correct category and group for the given description
    for group, categories in GROUPED_CATEGORIES.items():
        if predicted_category in categories:
            group_name = group
            category_name = predicted_category
            break
        else:
            group_name = 'Misc'
            category_name = 'Misc'
    return catgroup(group_name, category_name)

def create_catgroup_db(description, account=None):
    catgroup = get_cat_group(description, account)

    # Get or create the CategoryGroup instance
    group, _ = CategoryGroup.objects.get_or_create(name=catgroup.group)

    # Get or create the Category instance
    category, _ = Category.objects.get_or_create(name=catgroup.category, group=group)

    return category