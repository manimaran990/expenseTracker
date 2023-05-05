function drawGraph(graphData) {
    console.log('Graph data before plotting:', graphData);

    // Modify the trace object to add colors
    for (let i = 0; i < graphData.data.length; i++) {
        let trace = graphData.data[i];
        trace.marker = {
            color: []
        };

        for (let j = 0; j < trace.x.length; j++) {
            trace.marker.color.push(getColorForCategory(trace.x[j]));
        }
    }

    Plotly.newPlot('graph-container', graphData.data, graphData.layout);
}

function getColorForCategory(category) {
    const colors = {
        'Outing': '#1f77b4',
        'Trash': '#ff7f0e',
        'Entertainment - Other': '#2ca02c',
        'Parking': '#d62728',
        'Taxi': '#9467bd',
        'Entertainment': '#8c564b',
        'Hand loan': '#e377c2',
        'Gifts': '#7f7f7f',
        'Bus/train': '#bcbd22',
        'Liquor': '#17becf',
        'TV/Phone/Internet': '#6b8e23',
        'Rent': '#800000',
        'Household supplies': '#ff1493',
        'General': '#800080',
        'Insurance': '#cd5c5c',
        'Car': '#b8860b',
        'Dining out': '#008000',
        'Movies': '#4682b4',
        'Groceries': '#9acd32'
    };

    return colors[category] || '#808080'; // Default gray color if the category is not in the colors object
}

function populateExpenseTable(expenses, expenseTable) {
    var parsedTableJSON = expenses;
    console.log('expenses data before plotting:', parsedTableJSON);

    // Clear the existing data
    expenseTable.clear().draw();

    // Append new data
    for (var i = 0; i < expenses.length; i++) {
        var expense = expenses[i].fields;
        var row = '<tr><td>' + expense.date + '</td><td>' + expense.description + '</td><td>' + expense.category_name + '</td><td>' + expense.amount + '</td><td>' + expense.transaction_type + '</td><td><button class="btn btn-sm btn-primary edit-btn">Edit</button> <button class="btn btn-sm btn-danger delete-btn">Delete</button></td></tr>';
        expenseTable.row.add($(row)).draw(false);
    }
}

function drawPieCharts(debitData, creditData) {
    // Debit chart
    const debitTrace = {
        type: 'pie',
        labels: debitData.labels,
        values: debitData.values,
        marker: {
            colors: debitData.colors
        },
        hoverinfo: 'label+value'
    };

    const debitLayout = {
        title: 'Debit Expenses by Category',
    };

    Plotly.newPlot('debit-chart', [debitTrace], debitLayout);

    // Credit chart
    const creditTrace = {
        type: 'pie',
        labels: creditData.labels,
        values: creditData.values,
        marker: {
            colors: creditData.colors
        },
        hoverinfo: 'label+value'
    };

    const creditLayout = {
        title: 'Credit Expenses by Category',
    };

    Plotly.newPlot('credit-chart', [creditTrace], creditLayout);
}

$(document).ready(function () {

    $('input[type="file"]').on('change', function () {
        var fileName = $(this).val().split('\\').pop();
        $(this).siblings('.custom-file-label').addClass('selected').html(fileName);
    });

    $('#month-year-select').on('change', function () {
        var selectedMonthYear = $(this).val();
        console.log(selectedMonthYear);

        if (selectedMonthYear) {
            $.ajax({
                url: "{% url 'expense_tracker:expenses_summary_data' %}",
                data: {
                    'month_year': selectedMonthYear
                },
                success: function (data) {
                    console.log('AJAX response data:', data);
                    var parsedGraphJSON = JSON.parse(data.graphJSON);
                    var parsedTableJSON = JSON.parse(data.expenses);
                    console.log("after choosing dropdown: ", parsedTableJSON)
                    drawGraph(parsedGraphJSON);
                    populateExpenseTable(parsedTableJSON, expenseTable);
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    console.log('AJAX error:', textStatus, errorThrown);
                }
            });
        } else {
            // Handle empty selection if needed
        }
    });

    // Edit and Delete button event listeners
    $('body').on('click', '.edit-btn', function () {
        var row = $(this).closest('tr');
        var rowData = expenseTable.row(row).data();

        // Populate the form with the row data
        var form = $('#edit-expense-form');
        form.find('input[name="date"]').val(rowData[0]);
        form.find('input[name="description"]').val(rowData[1]);
        form.find('select[name="category"]').val(rowData[2]);
        form.find('input[name="amount"]').val(rowData[3]);
        form.find('select[name="transaction_type"]').val(rowData[4]);

        // Show the form
        $('#editExpenseModal').modal('show');
    });

    $('body').on('click', '.delete-btn', function () {
        var row = $(this).closest('tr');
        var rowData = expenseTable.row(row).data();

        // Send a request to delete the expense
        $.ajax({
            url: "{% url 'expense_tracker:delete_expense' %}",
            method: 'POST',
            data: {
                'expense_id': rowData[0],
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function (data) {
                if (data.status === 'success') {
                    // Remove the row from the table
                    expenseTable.row(row).remove().draw();
                } else {
                    alert('Error deleting expense');
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log('AJAX error:', textStatus, errorThrown);
            }
        });
    });

    // Add event listener for form submission
    $('#edit-expense-form').on('submit', function (event) {
        event.preventDefault();

        // Update the expense using an AJAX request
        const formData = new FormData(this);
        fetch('{% url "expense_tracker:update_expense" %}', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': '{{ csrf_token }}',
            },
        })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (data.status === 'success') {
                    // Refresh the page or update the table row
                    location.reload();
                } else {
                    alert('Error updating expense');
                }
            });
    });

});