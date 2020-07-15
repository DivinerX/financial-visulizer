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

    add_categories(expenses)

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
    income = df.copy()
    # Rename columns.
    income = income.drop(income[income.Amount < 0].index)
    income.columns = ['Date', 'Income', 'Category']
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

def add_categories(e_df):
    # e_df['Category'] = ''
    # print(e_df)
    # e_df = e_df.assign(Category=pd.Series(np.random.randn(len(e_df['Expense']))).values)
    # print(e_df)
    # for index in e_df.index:
    #     print(index)
    categories = []
    for index, row in e_df.iterrows():
        # Print column names.
        print([e_df.index.name] + e_df.columns.tolist())
        # Print single row of values.
        print(index, row['Expense'], row['Category'])
        # Print the categories to choose from.
        print(E_CATEGORIES)
        # Get user input and determine if it's valid else keep asking for input.
        category = input('Enter a category: ')
        while not good_input(category):
            category = input('Invalid category. Please choose one of the ' \
                             'numbers listed: ')
        categories.append(category)
        # Clear the screen between each iteration.
        os.system('clear')
    print(categories)

def good_input(category):
    return category.isdigit() and int(category) in E_CATEGORIES.keys()

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
