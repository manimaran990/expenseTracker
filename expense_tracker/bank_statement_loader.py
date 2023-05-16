import os
import re
import pandas as pd
import numpy as np
from expense_tracker.expense_utils import get_cat_group

def clean_description(description):
    cleaned_string = re.sub(r'\s+', ' ', description)
    return re.sub(r'[^a-zA-Z\s]', '', cleaned_string).strip()

class CIBC_handler:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.df = pd.read_csv(self.csv_file, names=["date", "description", "debit", "credit", "card"])
        self.df['card'] = self.df['card'].astype(str)
        self.df['card'] = self.df['card'].replace('nan', '')
        self.account = ""
        if not self.df.empty:
            card_value = self.df.loc[0, 'card']
            if card_value == "":
                self.account = "CIBC - Chequing"
            elif str(card_value).endswith('3603'):
                self.account = "CIBC - Credit"
    
    def add_category(self):
        self.df['category'] = self.df['description'].apply(lambda x: get_cat_group(x)[1])

    def view_transactions(self):
        print(self.df)

    def get_desc_category(self):
        self.df['description'] = self.df['description'].apply(clean_description)
        self.df['category'] = self.df.apply(lambda row: get_cat_group(row['description'], self.account)[1], axis=1)
        self.df[['description', 'category']].to_csv("/var/tmp/labeled_set.csv", index=False)


class AXIS_handler:
    pass

if __name__ == '__main__':
    csv_file = os.path.join(os.getcwd(), 'bank_transactions/cibc_cheq_all.csv')
    cibc_credit = CIBC_handler()
    cibc_credit.get_desc_category()