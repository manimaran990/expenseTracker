from django import forms
from django.forms import ModelForm, DateInput
from bootstrap4.widgets import RadioSelectButtonGroup
from .models import Expense, Investment, Category, InvestmentCategory, CURRENCY_TYPE_CHOICES, ACCOUNT_TYPES
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
    account = forms.ChoiceField(choices=ACCOUNT_TYPES)

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
    
class BankSelectionForm(forms.Form):
    BANK_CHOICES = [
        ('CIBC', 'CIBC'),
        ('Axis', 'Axis'),
        ('Other', 'Other'),
    ]
    bank = forms.ChoiceField(choices=BANK_CHOICES, widget=RadioSelectButtonGroup)

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}))

    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')
        if not csv_file:
            raise forms.ValidationError("No file uploaded!")
        return csv_file