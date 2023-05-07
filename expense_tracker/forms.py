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

        if transaction_type == "I":
            if not cleaned_data.get("investment_category"):
                raise forms.ValidationError("Investment category is required when transaction type is 'I'.")
            # Set owed_share to None when transaction_type is 'I'
            cleaned_data["owed_share"] = None
        else:
            if not cleaned_data.get("category"):
                raise forms.ValidationError("Expense category is required when transaction type is 'E'.")

        return cleaned_data