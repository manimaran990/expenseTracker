
"""
pip install numpy scipy scikit-learn pandas matplotlib
"""
import re
import csv
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle

# Step 1: Keyword mapping
def keyword_mapping(description):
    keywords = {
        'groceries': ['grocery', 'market', 'supermarket'],
        'dining out': ['restaurant', 'cafe', 'diner'],
        # ...
    }

    for category, words in keywords.items():
        if any(word in description.lower() for word in words):
            return category

    return None

# Step 2: Regular expressions
def regex_mapping(description):
    patterns = {
        'groceries': r'\b(grocery|market|supermarket)\b',
        'dining out': r'\b(restaurant|cafe|diner)\b',
        # ...
    }

    for category, pattern in patterns.items():
        if re.search(pattern, description, re.IGNORECASE):
            return category

    return None

def train_ml_model(X_train, y_train):
    vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
    classifier = RandomForestClassifier(n_estimators=100, random_state=42)
    model = make_pipeline(vectorizer, classifier)
    model.fit(X_train, y_train)
    return model

def predict_category_ml(description, model):
    return model.predict([description])[0]

# Step 4: NLP and AI model
# You can use GPT, BERT or any other NLP model for this step. The following is just a placeholder function.
def predict_category_nlp(description):
    return None

# Step 5: Combining all techniques
def categorize_expense(description, ml_model=None):
    # Keyword mapping
    category = keyword_mapping(description)
    if category is not None:
        return category

    # Regular expressions
    category = regex_mapping(description)
    if category is not None:
        return category

    # Machine learning
    if ml_model is not None:
        category = predict_category_ml(description, ml_model)
        if category is not None:
            return category

    # NLP and AI
    category = predict_category_nlp(description)
    if category is not None:
        return category

    # Default category if no match found
    return 'Uncategorized'

def train_model(labeled_dataset):
    data = []
    with open(labeled_dataset, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append((row.get('description'), row.get('category')))

    descriptions, categories = zip(*data)

    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(descriptions, categories, test_size=0.2, random_state=12)

    # Train the machine learning model
    ml_model = train_ml_model(X_train, y_train)

    # Assuming your trained model is named 'model'
    with open('trained_model.pkl', 'wb') as f:
        pickle.dump(ml_model, f)


# train_model(sys.argv[1])

# Test the model
# y_pred = [categorize_expense(desc, ml_model) for desc in X_test]

# print(classification_report(y_test, y_pred))

# # Predict a new description
# new_description = 'jacket'
# predicted_category = categorize_expense(new_description, ml_model)
# print(f'Predicted category for "{new_description}": {predicted_category}')