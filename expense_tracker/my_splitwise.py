import splitwise
from expense_tracker.config import consumer_key, consumer_secret, api_key
from collections import namedtuple

class SplitWise:
    def __init__(self):
        self.sObj = splitwise.Splitwise(consumer_key, consumer_secret,api_key=api_key)
        self.current_user = self.sObj.getCurrentUser()
        self.GroupsInfo = namedtuple('GroupsInfo', ['id', 'name', 'created_at'])
        self.ExpenseInfo = namedtuple('ExpenseInfo', ['id', 'description', 'date', 'currency', 'category', 'total_amount', 'your_share'])
        self.groups_list = []
        self.expense_list = []

    def get_groups(self):
        groups = self.sObj.getGroups()
        sorted_groups = sorted(groups, key=lambda x: x.created_at, reverse=True)
        for group in sorted_groups: 
            self.groups_list.append(self.GroupsInfo(group.id, group.name, group.created_at))
        return self.groups_list

    def get_expenses(self, group_id: str):
        #get expenses
        expenses = self.sObj.getExpenses(limit=999, group_id=group_id)
        for expense in expenses:
            expense_id = expense.id
            description = expense.description.strip()
            date = expense.getDate()
            currency = expense.getCurrencyCode()

            # Get the category
            category = expense.getCategory().getName()

            # Get the total amount of the expense
            total_amount = expense.getCost()

            # Calculate your share
            users = expense.users
            for user in users:
                if user.id == self.current_user.id:
                    your_share = float(user.net_balance)
                    if your_share > 0:
                        your_share = float(total_amount) - your_share

            expense_info = self.ExpenseInfo(expense_id, description, date, currency, category, total_amount, your_share)
            self.expense_list.append(expense_info)
        return self.expense_list


if __name__ == '__main__':
    sw = SplitWise()
    groups = sw.get_groups()
    expenses = sw.get_expenses(groups[0].id)
    print(groups)
    print(expenses)

