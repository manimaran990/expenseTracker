from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)

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
    date = models.DateField()

    def __str__(self):
        return f"{self.description} - {self.amount} - {self.date}"

class Expense(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('C', 'Credit'),
        ('D', 'Debit'),
        ('T', 'Transfer'),
        ('R', 'Refund')
    ]
    CURRENCY_TYPE_CHOICES = [
        ('CAD', 'Canadian Dollar'),
        ('INR', 'Indian Rupee')
    ]

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    currency = models.CharField(max_length=3, choices=CURRENCY_TYPE_CHOICES, default='CAD')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_TYPE_CHOICES, default='D')

    def __str__(self):
        return f"{self.description} - {self.amount} - {self.date}"