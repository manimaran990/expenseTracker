from django import forms
from .models import Expense, Category, InvestmentCategory

class ExpenseForm(forms.ModelForm):
    category = forms.ChoiceField(choices=(), required=True)

    class Meta:
        model = Expense
        fields = ['category', 'description', 'currency', 'amount', 'date', 'transaction_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        expense_categories = [(cat.id, cat.name) for cat in Category.objects.all()]
        investment_categories = [(f"i{cat.id}", cat.name) for cat in InvestmentCategory.objects.all()]
        self.fields['category'].choices = [('expense', '--- Expense Categories ---')] + expense_categories + [('investment', '--- Investment Categories ---')] + investment_categories
