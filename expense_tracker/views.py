from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.db.models import F, Func, Value
from django.db.models.functions import TruncMonth
from django.db.models import ExpressionWrapper, CharField
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core import serializers
from .serializers import expenses_to_json
from django.urls import reverse, reverse_lazy
from splitwise import Splitwise
from splitwise.expense import Expense
from .my_splitwise import SplitWise
from django.db.models import Sum
from datetime import date
import plotly.graph_objs as go
from datetime import date
from datetime import datetime
from .forms import CombinedForm, BankSelectionForm, CSVUploadForm
from .models import Expense, Investment, Category, CategoryGroup, InvestmentCategory, GROUPED_CATEGORIES
from .expense_utils import get_cat_group
from django.http import JsonResponse
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.utils as utils
import pandas as pd
import numpy as np
import json
import pickle
from .expense_utils import create_catgroup_db, clean_description

@login_required
def index(request):
    today = date.today()
    current_year = date.today().year
    current_month = today.month
    current_expenses = Expense.objects.filter(user=request.user, date__month=current_month, date__year=current_year)
    overall_expenses = Expense.objects.filter(user=request.user)
    current_investments = Investment.objects.filter(user=request.user, date__month=current_month, date__year=current_year)
    overall_investments = Investment.objects.filter(user=request.user)

    #paycheck object
    paycheck_category = Category.objects.get(name="Paycheck", group__name="Income")

    # Current month calculations
    credited_amount_cad = sum(exp.amount for exp in current_expenses if exp.transaction_type == 'C' and 
                              exp.currency == 'CAD' and exp.category == paycheck_category)
    credited_amount_inr = sum(exp.amount for exp in current_expenses if exp.transaction_type == 'C' and 
                              exp.currency == 'INR')

    debited_amount_cad = sum(exp.owed_share for exp in current_expenses if exp.transaction_type == 'D' and 
                             exp.currency == 'CAD')
    debited_amount_inr = sum(exp.owed_share for exp in current_expenses if exp.transaction_type == 'D' and 
                             exp.currency == 'INR')

    invested_amount_cad = sum(inv.amount for inv in current_investments if inv.currency == 'CAD')
    invested_amount_inr = sum(inv.amount for inv in current_investments if inv.currency == 'INR')

    outstanding_loans_cad = 0  # Calculate this based on your loan model if available, for CAD
    outstanding_loans_inr = 0  # Calculate this based on your loan model if available, for INR

     # Overall calculations
    overall_credited_amount_cad = sum(exp.amount for exp in overall_expenses if exp.transaction_type == 'C' and exp.currency == 'CAD' and exp.category == paycheck_category)
    overall_credited_amount_inr = sum(exp.amount for exp in overall_expenses if exp.transaction_type == 'C' and exp.currency == 'INR')

    overall_debited_amount_cad = sum(exp.owed_share for exp in overall_expenses if exp.transaction_type == 'D' and exp.currency == 'CAD')
    overall_debited_amount_inr = sum(exp.owed_share for exp in overall_expenses if exp.transaction_type == 'D' and exp.currency == 'INR')

    overall_invested_amount_cad = sum(inv.amount for inv in overall_investments if inv.currency == 'CAD')
    overall_invested_amount_inr = sum(inv.amount for inv in overall_investments if inv.currency == 'INR')

    context = {
        'current_date': today,
        'current_month': current_month,
        'credited_amount_cad': credited_amount_cad,
        'credited_amount_inr': credited_amount_inr,
        'debited_amount_cad': debited_amount_cad,
        'debited_amount_inr': debited_amount_inr,
        'invested_amount_cad': invested_amount_cad,
        'invested_amount_inr': invested_amount_inr,
        'outstanding_loans_cad': outstanding_loans_cad,
        'outstanding_loans_inr': outstanding_loans_inr,
        'overall_credited_amount_cad': overall_credited_amount_cad,
        'overall_credited_amount_inr': overall_credited_amount_inr,
        'overall_debited_amount_cad': overall_debited_amount_cad,
        'overall_debited_amount_inr': overall_debited_amount_inr,
        'overall_invested_amount_cad': overall_invested_amount_cad,
        'overall_invested_amount_inr': overall_invested_amount_inr,
    }

    return render(request, 'expense_tracker/index.html', context)

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = CombinedForm(request.POST)
        if form.is_valid():
            transaction_type = form.cleaned_data['transaction_type']
            if transaction_type == 'I':
                 # Create an Investment instance
                investment = Investment(
                    user=request.user,
                    investment_category=form.cleaned_data['category'],
                    description=form.cleaned_data['description'],
                    amount=form.cleaned_data['amount'],
                    date=form.cleaned_data['date'],
                )
                investment.save()
                messages.success(request, 'Investment successfully added')
            else:
                # Create an Expense instance
                expense = Expense(
                    user=request.user,
                    category=form.cleaned_data['category'],
                    description=form.cleaned_data['description'],
                    currency=form.cleaned_data['currency'],
                    amount=form.cleaned_data['amount'],
                    owed_share=form.cleaned_data['owed_share'],
                    date=form.cleaned_data['date'],
                    transaction_type=transaction_type,
                    account=form.cleaned_data['account']
                )
                expense.save()
                messages.success(request, 'Expense successfully added')
            return redirect('expense_tracker:add_expense')  # Replace with the correct URL pattern name for expense list
    else:
        form = CombinedForm()

    return render(request, 'expense_tracker/add_expense.html', {'form': form})

@login_required
def expense_summary(request):
    current_month = date.today().month
    current_year = date.today().year
    categories = Category.objects.all()

    #default values to show on load
    account = 'Splitwise'
    transaction_type = 'D'
    expenses = Expense.objects.filter(user=request.user, date__year=current_year, date__month=current_month
                                      , category__in=categories, account=account, transaction_type=transaction_type)
    expenses = expenses.exclude(description='Payment')

    accounts = Expense.objects.values('account').distinct()
    transaction_types = Expense.objects.values('transaction_type').distinct()

    # Get unique month-year values
    month_years = Expense.objects.filter(user=request.user).annotate(
        month_years=ExpressionWrapper(TruncMonth('date'), output_field=CharField())
    ).values('month_years').distinct().order_by('-month_years')

    expenses_by_grouped_category = []

    for category, subcategories in GROUPED_CATEGORIES.items():
        category_expenses = []

        for subcategory in subcategories:
            subcategory_expenses = sum(exp.owed_share for exp in expenses if exp.category.name == subcategory)
            category_expenses.append(subcategory_expenses)
        expenses_by_grouped_category.append({
            'category': category,
            'total': sum(category_expenses),
            'subcategories': category_expenses
        })

    fig = go.Figure()

    for idx, category in enumerate(expenses_by_grouped_category):
        for i, subcategory_expense in enumerate(category['subcategories']):
            fig.add_trace(go.Bar(
                x=[category['category']],
                y=[subcategory_expense],
                name=GROUPED_CATEGORIES[category['category']][i],
                text=[subcategory_expense],
                textposition='auto',
                legendgroup=category['category'],
            ))

    fig.update_layout(
        title="Expenses by Grouped Category",
        xaxis_title="Grouped Categories",
        yaxis_title="Expenses",
        barmode='stack',
    )

    if not expenses_by_grouped_category:
        fig.add_annotation(
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            text="No data available",
            showarrow=False,
            font_size=18,
            opacity=0.7
        )

    graphJSON = json.dumps(fig, cls=utils.PlotlyJSONEncoder)

    serialized_categories = serializers.serialize('json', categories)
    # import pdb; pdb.set_trace
    context = {
        'month_years': month_years,
        'graphJSON': graphJSON,
        'expenses': expenses_to_json(expenses),
        'categories': categories,
        'accounts': accounts,
        'transaction_types': transaction_types
    }
    return render(request, 'expense_tracker/expense_summary.html', context)

@login_required
def expenses_summary_data(request):
    month_year = request.GET.get('month_year')
    account = request.GET.get('account')
    transaction_type = request.GET.get('transaction_type')

    if month_year and '-' in month_year and len(month_year) == 7:
        year, month = month_year.split('-')
        year = int(year)
        month = int(month)
    else:
        today = datetime.today()
        year = today.year
        month = today.month

    # Initial query
    expenses = Expense.objects.filter(user=request.user)

    if month_year:
        if len(month_year) == 1:
            year, month = today.year, today.month
        else:
            year, month = map(int, month_year.split('-'))
        expenses = expenses.filter(date__year=year, date__month=month)

    if account:
        expenses = expenses.filter(account=account)

    if transaction_type:
        expenses = expenses.filter(transaction_type=transaction_type)

    categories = Category.objects.all()
    # expenses = Expense.objects.filter(user=request.user, date__year=year, date__month=month, category__in=categories)
    expenses = expenses.exclude(description='Payment')

    expenses_by_grouped_category = []

    for category, subcategories in GROUPED_CATEGORIES.items():
        category_expenses = []

        for subcategory in subcategories:
            subcategory_expenses = sum(exp.owed_share for exp in expenses if exp.category.name == subcategory)
            category_expenses.append(subcategory_expenses)
        expenses_by_grouped_category.append({
            'category': category,
            'total': sum(category_expenses),
            'subcategories': category_expenses
        })

    fig = go.Figure()

    for idx, category in enumerate(expenses_by_grouped_category):
        for i, subcategory_expense in enumerate(category['subcategories']):
            fig.add_trace(go.Bar(
                x=[category['category']],
                y=[subcategory_expense],
                name=GROUPED_CATEGORIES[category['category']][i],
                text=[subcategory_expense],
                textposition='auto',
                legendgroup=category['category'],
            ))

    fig.update_layout(
        title="Expenses by Grouped Category",
        xaxis_title="Grouped Categories",
        yaxis_title="Expenses",
        barmode='stack',
    )

    graphJSON = json.dumps(fig, cls=utils.PlotlyJSONEncoder)

    serialized_categories = serializers.serialize('json', categories)
    data = {
        'graphJSON': graphJSON,
        'expenses': expenses_to_json(expenses),
        'categories': serialized_categories,
    }
    return JsonResponse(data)

@login_required
def splitwise(request):
    splitwise_obj = SplitWise()  # Initialize the SplitWise class
    groups_list = splitwise_obj.get_groups()  # Get the list of groups

    context = {
        'groups_list': groups_list
    }
    
    messages.success(request, 'Sync operation completed successfully!')
    return render(request, 'expense_tracker/splitwise.html', context)

@login_required
def sync_expenses(request):
    group_id = request.GET.get('group_id')
    splitwise_obj = SplitWise()  # Initialize the SplitWise class
    expenses_list = splitwise_obj.get_expenses(group_id)

    # Save the expenses in the Expense model
    for expense_info in expenses_list:
        if not Expense.objects.filter(id=expense_info.id).exists():
            category = create_catgroup_db(expense_info.description)
            # Create a new category if it doesn't exist
            category, _ = Category.objects.get_or_create(name=category.name)
            expense = Expense(
                id=expense_info.id,
                user=request.user,
                date = datetime.strptime(expense_info.date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d"),
                description=expense_info.description,
                category=category,
                amount=expense_info.total_amount,
                owed_share=expense_info.owed_share,
                currency=expense_info.currency,
                transaction_type='D', #we only track Debited expenses here
                account='Splitwise' #for splitwise expenses it will be Splitwise
            )
            expense.save()

    return JsonResponse({"status": "success"})

@login_required
@csrf_exempt
def create_expense(request):
    if request.method == 'POST':
        # Extract data from the request
        date = request.POST.get('date')
        description = request.POST.get('description')
        category_name = request.POST.get('category')
        amount = request.POST.get('amount')
        transaction_type = request.POST.get('transaction_type')
        account = request.POST.get('account')
        
        # Create and save the new expense
        user = request.user
        category, created = Category.objects.get_or_create(name=category_name)
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        expense = Expense(user=user, category=category, description=description, amount=amount, date=date_obj, transaction_type=transaction_type, account=account)
        expense.save()
        
        return JsonResponse({'status': 'success'})

@login_required
@csrf_exempt
def update_expense(request):
    if request.method == 'POST':
        # Extract data from the request
        expense_id = request.POST.get('expense_id')
        date = request.POST.get('date')
        description = request.POST.get('description')
        category_name = request.POST.get('category')
        amount = request.POST.get('amount')
        owed_share = request.POST.get('owed_share')
        transaction_type = request.POST.get('transaction_type')
        account = request.POST.get('account')
        
        # Update the existing expense
        user = request.user
        expense = Expense.objects.get(id=expense_id, user=user)
        category, created = Category.objects.get_or_create(name=category_name)
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        expense.date = date_obj
        expense.description = description
        expense.category = category
        expense.amount = amount
        expense.owed_share = owed_share
        expense.transaction_type = transaction_type
        expense.account = account
        expense.save()
        
        return JsonResponse({'status': 'success'})

@login_required
def delete_expense(request):
    if request.method == 'POST':
        # Extract data from the request
        expense_id = request.POST.get('expense_id')
        
        # Delete the expense
        user = request.user
        expense = Expense.objects.get(id=expense_id, user=user)
        expense.delete()
        
        return JsonResponse({'status': 'success'})

@login_required
def get_expense_categories(request):
    categories = Category.objects.values('id', 'name')
    return JsonResponse(list(categories), safe=False)

@login_required
def get_expense_data(request):
    current_month = date.today().month
    current_year = date.today().year
    
    expenses = Expense.objects.filter(user=request.user, date__month=current_month, date__year=current_year)
    investments = Investment.objects.filter(user=request.user, date__month=current_month, date__year=current_year)
    debit_expenses = expenses.filter(transaction_type='D').values('category__name').annotate(total_amount=Sum('amount'))
    credit_expenses = expenses.filter(transaction_type='C').values('category__name').annotate(total_amount=Sum('amount'))
    overall_debit_expenses = Expense.objects.filter(user=request.user, transaction_type='D').values('category__name').annotate(total_amount=Sum('owed_share')).order_by('-total_amount')
    overall_credit_expenses = Expense.objects.filter(user=request.user, transaction_type='C').values('category__name').annotate(total_amount=Sum('owed_share')).order_by('-total_amount')


    return JsonResponse({
        'debit_expenses': list(debit_expenses),
        'credit_expenses': list(credit_expenses),
        'overall_debit_expenses': list(overall_debit_expenses),
        'overall_credit_expenses': list(overall_credit_expenses),
    }, safe=False)

@login_required
def get_investment_categories(request):
    categories = InvestmentCategory.objects.values('id', 'name')
    return JsonResponse(list(categories), safe=False)


class BankStatementLoaderView(LoginRequiredMixin, FormView):
    template_name = 'expense_tracker/banking_loader.html'
    form_class = BankSelectionForm
    success_url = reverse_lazy('expense_tracker:bank_statement_loader')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['csv_form'] = CSVUploadForm(self.request.POST, self.request.FILES)
        else:
            data['csv_form'] = CSVUploadForm()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        csv_form = context['csv_form']
        if csv_form.is_valid():
            bank = form.cleaned_data.get('bank')

            if bank == 'CIBC':
                form_class = CSVUploadForm
                form = form_class(self.request.POST, self.request.FILES)

                if form.is_valid():
                    csv_file = form.cleaned_data.get('csv_file')
                    df = pd.read_csv(csv_file, names=["date", "description", "debit", "credit", "card"])
                    df['card'] = df['card'].astype(str)
                    df['card'] = df['card'].replace('nan', '')

                    df['account'] = np.where(df['card'] == '', "CIBC - Chequing", np.where(df['card'].str.endswith('3603'), "CIBC - Credit", ""))
                    
                    for index, row in df.iterrows():
                        account = row['account']
                        user = self.request.user
                        description = clean_description(row['description'])
                        category = create_catgroup_db(description, account)
                        currency = 'CAD'
                        date = row['date']
                        amount = None
                        transaction_type = None
                        if not np.isnan(row['debit']):
                            amount = row['debit']
                            transaction_type = 'D'
                            owed_share = row['debit']
                        else:
                            amount = row['credit']
                            transaction_type = 'C'
                            owed_share = 0.0

                        Expense.objects.create(date=date, 
                                               user=user,
                                               description=description, 
                                               amount=amount,
                                               transaction_type=transaction_type,
                                               owed_share=owed_share,
                                               currency=currency, 
                                               category=category, 
                                               account=account)

        return super().form_valid(form)