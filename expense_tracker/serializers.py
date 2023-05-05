# expense_tracker/serializers.py

import json

def expenses_to_json(expenses):
    expense_list = []

    for expense in expenses:
        expense_data = {
            "model": "expense_tracker.expense",
            "pk": expense.id,
            "fields": {
                "user": expense.user.id,
                "category": expense.category.id,
                "category_name": expense.category.name,
                "description": expense.description,
                "currency": expense.currency,
                "amount": str(expense.amount),
                "date": expense.date.strftime("%Y-%m-%d"),
                "transaction_type": expense.transaction_type,
            },
        }
        expense_list.append(expense_data)

    return json.dumps(expense_list)
