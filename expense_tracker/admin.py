from django.contrib import admin
from .models import Expense, Investment, Category, InvestmentCategory

# Register your models here.
admin.site.register(Expense)
admin.site.register(Investment)
admin.site.register(Category)
admin.site.register(InvestmentCategory)