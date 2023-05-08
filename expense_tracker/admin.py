from django.contrib import admin
from .models import Expense, Investment, Category, InvestmentCategory, CategoryGroup

# Register your models here.
admin.site.register(Expense)
admin.site.register(Investment)
admin.site.register(Category)
admin.site.register(CategoryGroup)
admin.site.register(InvestmentCategory)