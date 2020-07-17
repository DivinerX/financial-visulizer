import argparse
import csv
import os

import numpy as np
import pandas as pd

from categories import E_CATEGORIES, I_CATEGORIES


def organize_files(exceptions_file, *args):
    # Read and concatenate files into single dataframe.
    raw_df = pd.concat(map(pd.read_csv, *args))
    if debug:
        # Can't use a starred expression in fstrings so I used format this time.
        print('Files given: {}'.format(*args))
        print(f'Raw dataframe:\n{raw_df}\n')
    filtered_df = remove_exceptions(exceptions_file, raw_df)
    trimmed_df = pd.DataFrame(filtered_df, columns = ['Posting Date', 'Amount',
                                                      'Extended Description'])
    if debug:
        print(f'Trimmed dataframe:\n{trimmed_df}\n')
    income = organize_income(trimmed_df)
    expenses = organize_expenses(trimmed_df)

    add_categories(income, I_CATEGORIES)
    add_categories(expenses, E_CATEGORIES)

def remove_exceptions(exceptions_file, raw_df):
    exceptions = []
    with open(exceptions_file, newline='') as f:
        lines = csv.reader(f)
        iterlines = iter(lines)
        for line in iterlines:
            # Get the exception from each line.
            exceptions.append(line[0].strip())
    if debug:
        print(f'Exceptions: {exceptions}')
    for exception in exceptions:
        if debug:
            # Print the rows about to be removed from the dataframe.
            print(raw_df[raw_df['Extended Description'].str.contains(exception)])
        # Rewrite the dataframe with the rows containing exceptions now removed.
        raw_df = raw_df[~raw_df['Extended Description'].str.contains(exception)]
    return raw_df

def organize_income(df):
    # Create a deep copy of the dataframe.
    income = df.copy()
    # Remove all rows with negative numbers.
    income = income[income.select_dtypes(include=[np.number]).ge(0).all(1)]
    # Rename columns.
    income.columns = ['Date', 'Income', 'Category']
    income['From'] = ''
    income['Description'] = ''
    # Convert dates to format that pandas can work with.
    income['Date'] = pd.to_datetime(income['Date'])
    # Make the Date column the new index.
    income.index = income['Date']
    del income['Date']
    income = income.sort_index()

    if debug:
        print(f'Organized income:\n{income}\n')
    return income

def organize_expenses(expenses):
    # Rename columns.
    expenses.columns = ['Date', 'Expense', 'Category']
    expenses['To'] = ''
    expenses['Description'] = ''
    # Convert dates to format that pandas can work with.
    expenses['Date'] = pd.to_datetime(expenses['Date'])
    # Make the Date column the new index.
    expenses.index = expenses['Date']
    del expenses['Date']
    expenses = expenses.sort_index()

    # Remove all rows with positive numbers.
    expenses = expenses.drop(expenses[expenses.Expense > 0].index)
    # TODO: Determine if needed.
    # Convert all negatives prices to positive.
    # expenses['Expense'] = expenses['Expense'].abs()
    if debug:
        print(f'Organized expenses:\n{expenses}\n')
    return expenses

def add_categories(df, category_dict):
    categories = []
    recipients = []
    descriptions = []
    type = None
    for index, row in df.iterrows():
        # Print column names.
        print([df.index.name] + df.columns.tolist())
        # Print single row of values.
        print(f'[{index}, {row[0]}, {row[1]}]')
        # Print the expense categories to choose from.
        print(category_dict)
        category = input('Enter a category: ')
        while not good_category(category, category_dict):
            category = input('Invalid category. Please choose one of the ' \
                             'numbers listed: ')
        categories.append(category_dict[int(category)])
        to_from = input(f'{df.columns[2]}: ')
        while to_from is '' or to_from.isspace():
            to_from = input('Please enter a value, any value: ')
        recipients.append(to_from)
        descriptions.append(input('(Optional) Description: '))
        # Clear the screen between each iteration.
        os.system('clear')
    # Add lists to the dataframe.
    df = df.assign(Category = categories)
    if list(df.columns)[0] == 'Expense':
        df = df.assign(To = recipients)
    else:
        df = df.assign(From = recipients)
    df = df.assign(Description = descriptions)

    if debug:
        print(f'Categories:\n{categories}\n')
        print(f'Dataframe with updated categories:\n{df}\n')

def good_category(category, category_dict):
    return category.isdigit() and int(category) in category_dict.keys()

def main():
    parser = argparse.ArgumentParser(description='Organize raw finances.')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable \
                                                                    debug \
                                                                    output.')
    parser.add_argument('-f', '--files', nargs='*', required=True,
                        help='CSV file(s) containing finances.')
    parser.add_argument('-e', '--exceptions', help='A CSV of newline separated \
                                                    descriptions that if found \
                                                    will get removed from the \
                                                    data.')
    args = parser.parse_args()
    global debug
    debug = args.debug

    organize_files(args.exceptions, args.files)

if __name__ == "__main__":
    main()
