from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.db.models import F, Func, Value
from django.db.models.functions import TruncMonth
from django.db.models import ExpressionWrapper, CharField
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core import serializers
from .serializers import expenses_to_json
from django.urls import reverse
from splitwise import Splitwise
from splitwise.expense import Expense
from .my_splitwise import SplitWise
from .models import Expense, Investment
from datetime import date
import plotly.graph_objs as go
from datetime import date
from datetime import datetime
from .forms import CombinedForm
from .models import Expense, Investment, Category, InvestmentCategory
from django.http import JsonResponse
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.utils as utils
import pandas as pd
import json
import pickle

def load_trained_model(model_path):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

def get_category(description):
    predicted_category = model.predict([description])[0]
    return predicted_category

model_path = 'expense_tracker/trained_model.pkl'
model = load_trained_model(model_path)

@login_required
def index(request):
    today = date.today()
    current_month = today.month
    expenses = Expense.objects.filter(user=request.user, date__month=current_month)
    investments = Investment.objects.filter(user=request.user, date__month=current_month)

    credited_amount = sum(exp.amount for exp in expenses if exp.transaction_type == 'C')
    debited_amount = sum(exp.amount for exp in expenses if exp.transaction_type == 'D')
    invested_amount = sum(inv.amount for inv in investments)
    outstanding_loans = 0  # Calculate this based on your loan model if available

    # Generate the graph data
    data = [
        go.Bar(
            x=['Credited', 'Debited', 'Invested', 'Outstanding Loans'],
            y=[credited_amount, debited_amount, invested_amount, outstanding_loans],
            marker=dict(color='rgb(142, 68, 173)')
        )
    ]

    context = {
        'current_date': today,
        'current_month': current_month,
        'credited_amount': credited_amount,
        'debited_amount': debited_amount,
        'invested_amount': invested_amount,
        'outstanding_loans': outstanding_loans,
        'graph_data': data,
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
                )
                expense.save()
                messages.success(request, 'Expense successfully added')
            return redirect('expense_tracker:add_expense')  # Replace with the correct URL pattern name for expense list
    else:
        form = CombinedForm()

    return render(request, 'expense_tracker/add_expense.html', {'form': form})

@login_required
def expense_summary(request):
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']
        if csv_file:
            # Read the CSV file using pandas
            df = pd.read_csv(csv_file)

            mani_df = df[["Date", "Description", "Category", "Cost", "Currency", "mani maran"]]

            # Replace 'your_username' with the currently logged in user's username
            user = request.user

            for index, row in mani_df.iterrows():
                dt, description, category_name, amount, currency, mani_maran = row
                category, created = Category.objects.get_or_create(name=category_name)
                date_obj = datetime.strptime(dt, '%Y-%m-%d')
                amount_mani_maran = float(mani_maran)
                amount_mani_maran = float(amount) - amount_mani_maran if amount_mani_maran > 0 else amount_mani_maran
                transaction_type = 'debit' if amount_mani_maran < 0 else 'credit'
                expense = Expense(user=user, category=category, currency=currency, description=description, amount=abs(amount_mani_maran), date=date_obj, transaction_type=transaction_type)
                expense.save()

            messages.success(request, 'All records have been successfully added to the Expense table.')
        else:
            messages.warning(request, 'No file was uploaded. Please choose a CSV file.')

        # Redirect to the same page to avoid re-uploading on page refresh
        return HttpResponseRedirect(reverse('expense_tracker:expense_summary'))
    else:
        current_month = date.today().month
        current_year = date.today().year
        categories = Category.objects.all()
        expenses = Expense.objects.filter(user=request.user, date__year=current_year, date__month=current_month, category__in=categories)
        expenses = expenses.exclude(description='Payment')

        # Get unique month-year values
        month_years = Expense.objects.filter(user=request.user).annotate(
        month_years=ExpressionWrapper(TruncMonth('date'), output_field=CharField())
    ).values('month_years').distinct().order_by('-month_years')
        expenses_by_category = []
        for category in categories:
            expenses_by_category.append({
                'category': category.name,
                'total': sum(exp.owed_share for exp in expenses if exp.category == category)
            })

        if expenses_by_category:
            fig = px.bar(expenses_by_category, x='category', y='total', text='total', labels={'total': 'Expenses', 'category': 'Categories'}, title='Expenses by Category')
        else:
            fig = go.Figure()
            fig.update_layout(title="Expenses by Category", xaxis_title="Categories", yaxis_title="Expenses")
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
        
        # serialized_expenses = serializers.serialize('json', expenses)
        serialized_categories = serializers.serialize('json', categories)
        context = {
            'month_years': month_years,
            'graphJSON': graphJSON,
            'expenses': expenses_to_json(expenses),
            'categories': categories,
        }
        return render(request, 'expense_tracker/expense_summary.html', context)

@login_required
def expenses_summary_data(request):
    month_year = request.GET.get('month_year', None)
    
    if month_year:
        year, month = month_year.split('-')
        year = int(year)
        month = int(month)
    else:
        today = datetime.today()
        year = today.year
        month = today.month

    categories = Category.objects.all()
    expenses = Expense.objects.filter(user=request.user, date__year=year, date__month=month, category__in=categories)
    expenses = expenses.exclude(description='Payment')

    expenses_by_category = []
    for category in categories:
        expenses_by_category.append({
            'category': category.name,
            'total': sum(exp.owed_share for exp in expenses if exp.category == category)
        })

    fig = px.bar(expenses_by_category, x='category', y='total', text='total', labels={'total': 'Expenses', 'category': 'Categories'}, title='Expenses by Category')
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
            category = get_category(expense_info.description)
            # Create a new category if it doesn't exist
            category, _ = Category.objects.get_or_create(name=category)
            expense = Expense(
                id=expense_info.id,
                user=request.user,
                date = datetime.strptime(expense_info.date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d"),
                description=expense_info.description,
                category=category,
                amount=expense_info.total_amount,
                owed_share=expense_info.owed_share,
                currency=expense_info.currency,
                transaction_type='D',
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
        
        # Create and save the new expense
        user = request.user
        category, created = Category.objects.get_or_create(name=category_name)
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        expense = Expense(user=user, category=category, description=description, amount=amount, date=date_obj, transaction_type=transaction_type)
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
def get_investment_categories(request):
    categories = InvestmentCategory.objects.values('id', 'name')
    return JsonResponse(list(categories), safe=False)