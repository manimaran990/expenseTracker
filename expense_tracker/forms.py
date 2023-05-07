from django import forms
from django.forms import ModelForm, DateInput
from .models import Expense, Investment, Category, InvestmentCategory, CURRENCY_TYPE_CHOICES
from datetime import date

class DateInput(forms.DateInput):
    input_type = 'date'

class CombinedForm(forms.Form):
    # Common fields
    description = forms.CharField()
    amount = forms.DecimalField()
    currency = forms.ChoiceField(choices=CURRENCY_TYPE_CHOICES)
    date = forms.DateField(widget=DateInput(attrs={'value': date.today().strftime('%Y-%m-%d')}))
    transaction_type = forms.ChoiceField(choices=Expense.TRANSACTION_TYPE_CHOICES)
    owed_share = forms.DecimalField(required=False, initial=0.0)

    # Expense fields
    category = forms.ModelChoiceField(queryset=Category.objects.all())

    # Investment fields
    investment_category = forms.ModelChoiceField(queryset=InvestmentCategory.objects.all(), required=False)

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get("transaction_type")

        if transaction_type == "I" or transaction_type == "C" or transaction_type == "R":
            cleaned_data['owed_share'] = 0.0

        return cleaned_data