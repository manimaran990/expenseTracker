from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "expense_tracker"
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='expense_tracker/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.index, name='index'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('expense_summary/', views.expense_summary, name='expense_summary'),
    path('expenses_summary_data/', views.expenses_summary_data, name='expenses_summary_data'),
    path('splitwise/', views.splitwise, name='splitwise'),
    path('sync_expenses/', views.sync_expenses, name='sync_expenses'),
    path('create_expense/', views.create_expense, name='create_expense'),
    path('update_expense/', views.update_expense, name='update_expense'),
    path('delete_expense/', views.delete_expense, name='delete_expense'),
    path('get_expense_categories/', views.get_expense_categories, name='get_expense_categories'),
    path('get_investment_categories/', views.get_investment_categories, name='get_investment_categories'),
    path('get_expense_data/', views.get_expense_data, name='get_expense_data'),
]