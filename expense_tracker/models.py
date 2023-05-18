from django.db import models
from django.contrib.auth.models import User

GROUPED_CATEGORIES = {
    'Transit': ['Gas/fuel', 'Taxi', 'Car', 'Parking', 'Flight'],
    'Refund': ['Refund'],
    'Online': ['Shopping', 'Subscription'],
    'Banking': ['Payment', 'Interest', 'Service charge', 'Transfer', 'Withdraw', 'Bill Payment'],
    'Shopping': ['Shopping - General', 'Household supplies', 'Groceries', 'Clothing', 'Furnitures', 'Electronics', 'Games', 'Sports'],
    'Food': ['Fruits', 'Fish/Meat', 'Dining out', 'Restaurant'],
    'Income': ['Paycheck', 'Dividends'],
    'Utility': ['Trash', 'TV/Phone/Internet', 'Rent'],
    'Entertainment': ['Entertainment - Other', 'Movies', 'Entertainment'],
    'Insurance': ['Insurance', 'TermInsurance'],
    'Gifts': ['Gifts', 'Cake'],
    'Liquor': ['Liquor'],
    'General': ['General'],
    'Public Transport': ['Bus/train'],
    'Investment': ['MF', 'ETF', 'Gold', 'Crypto', 'PPF'],
    'Misc': ['Misc']
}

ACCOUNT_TYPES = [
    ('AXIS - Debit', 'Axis bank Debit account'),
    ('AXIS - Credit', 'Axis bank Credit account'),
    ('CIBC - Chequing', 'CIBC bank Chequing account'),
    ('CIBC - Savings', 'CIBC bank Savings account'),
    ('CIBC - Credit', 'CIBC bank Credit account'),
    ('Splitwise', 'Splitwise Group Expenses'),
    ('Other', 'Other accounts'),
]

CURRENCY_TYPE_CHOICES = [
        ('CAD', 'Canadian Dollar'),
        ('INR', 'Indian Rupee')
    ]

class CategoryGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True, blank=True)  # New field

    def __str__(self):
        return self.name
    
class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True, blank=True)  # New field
    group = models.ForeignKey(CategoryGroup, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class InvestmentCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Investment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    investment_category = models.ForeignKey(InvestmentCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_TYPE_CHOICES, default='INR')
    date = models.DateField()

    def __str__(self):
        return f"{self.description} - {self.amount} - {self.date}"

class Expense(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('C', 'Credit'),
        ('D', 'Debit'),
        ('T', 'Transfer'),
        ('R', 'Refund'),
        ('I', 'Investment')
    ]

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    currency = models.CharField(max_length=3, choices=CURRENCY_TYPE_CHOICES, default='CAD')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    owed_share = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    date = models.DateField()
    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_TYPE_CHOICES, default='D')
    account = models.CharField(max_length=15, choices=ACCOUNT_TYPES, default='Other')

    def __str__(self):
        return f"{self.description} - {self.amount} - {self.date}"