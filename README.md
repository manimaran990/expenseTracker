# Expense Tracker

This is a Django-based web application for tracking personal expenses. It allows users to upload a CSV file and sync between splitwise expenses, and then provides a summary of their expenses by category and month. Users can also add, edit, and delete their expenses within the app.

## Features
- Users can upload a CSV file with their expenses
- Expenses are automatically added to the app's database and categorized by category
- Users can view a summary of their expenses by category and month in a bar graph
- Users can add new expenses to the app by filling out a form
- Users can edit or delete their expenses using an inline table
- Users can create new categories or investment types while adding an expense
- App is deployed on PythonAnywhere

## Technologies Used
- Python
- Django
- HTML/CSS
- Bootstrap
- JavaScript
- jQuery
- Plotly

## Installation
To run this app on your local machine, follow these steps:

Clone the repository to your local machine using git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY

Install the required packages using pip install -r requirements.txt

Create a new database by running python manage.py migrate

Run the server using python manage.py runserver

Access the app by visiting http://127.0.0.1:8000/etracker in your web browser

## Usage

### Uploading Expenses
Click on the "Upload Expenses" button on the home page

### Select a CSV file to upload

Click "Submit" to upload the file

### Viewing Expense Summary
Click on the "View Expenses" button on the home page

View the summary of expenses by category and month in a bar graph

### Adding Expenses
Click on the "Add Expense" button on the home page

Fill out the form with the required information, including the category

Click "Submit" to add the expense

### Editing Expenses
Click on the "Edit" button on the expense table row that you want to edit

Make the desired changes to the form

Click "Submit" to save the changes

### Deleting Expenses
Click on the "Delete" button on the expense table row that you want to delete

Confirm that you want to delete the expensez

The expense will be removed from the table and the database

## License
This project is licensed under the terms of the MIT license.
