import argparse
import csv
import os

import numpy as np
import pandas as pd

from categories import E_CATEGORIES, I_CATEGORIES


def organize_data(exceptions_file, *args):
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

    # Get the user to fill out 'Category', 'To/From', and 'Description' columns.
    income = fill_remaining_columns(income, I_CATEGORIES)
    expenses = fill_remaining_columns(expenses, E_CATEGORIES)

    if debug:
        print(f'Final income dataframe:\n{income}\n')
        print(f'Final expenses dataframe:\n{expenses}\n')

    return income, expenses

def remove_exceptions(exceptions_file, raw_df):
    exceptions = []
    with open(exceptions_file, newline='') as f:
        lines = csv.reader(f)
        iterlines = iter(lines)
        for line in iterlines:
            # Get the exception from each line.
            exceptions.append(line[0].strip())

    if debug:
        print(f'Exceptions: {exceptions}\n')

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

    if debug:
        print(f'Organized expenses:\n{expenses}\n')
    return expenses

def fill_remaining_columns(df, category_dict):
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
        # Get user input to fill in the remaining columns.
        get_input(df, category_dict, categories, recipients, descriptions)
    # Add lists to the dataframe.
    df = df.assign(Category = categories)
    if list(df.columns)[0] == 'Expense':
        df = df.assign(To = recipients)
    else:
        df = df.assign(From = recipients)
    df = df.assign(Description = descriptions)

    if debug:
        print(f'Entered categories:\n{categories}\n')

    return df

def get_input(df, category_dict, categories, recipients, descriptions):
    category = input('Enter a category: ')
    while not good_category(category, category_dict):
        category = input('Invalid category. Please choose one of the ' \
                         'numbers listed: ')
    categories.append(category_dict[int(category)])
    # Get the third column name, it'll either be 'To' or 'From'.
    to_from = input(f'{df.columns[2]}: ')
    # While the input is an empty string or whitespace, ask for input again.
    while to_from is '' or to_from.isspace():
        to_from = input('Please enter a value, any value: ')
    recipients.append(to_from)
    descriptions.append(input('(Optional) Description: '))
    # Clear the screen between each iteration.
    os.system('clear')

def good_category(category, category_dict):
    return category.isdigit() and int(category) in category_dict.keys()

def write_file(df, file_path, write_mode):
    # If the file already exists, don't write column names since presumably they
    # are already in the file.
    header = None
    if not os.path.isfile(file_path):
        header = True

    # Terminal color codes.
    bold = '\033[1m'
    reset = '\x1b[0m'

    df.to_csv(path_or_buf=file_path, header=header, mode=write_mode)
    print(f'{list(df.columns)[0]} dataframe written in "{write_mode}" mode ' \
          f'to {bold}{file_path}{reset}.')

# def main():
#     parser = argparse.ArgumentParser(description='Organize raw finances.')
#     parser.add_argument('-d', '--debug', action='store_true', help='enable ' \
#                         'debug output')
#     parser.add_argument('-f', '--files', nargs='*', required=True,
#                         help='CSV file(s) containing finances')
#     parser.add_argument('-e', '--exceptions', help='a CSV of newline ' \
#                         'separated descriptions that if found will get ' \
#                         'removed from the data')
#     parser.add_argument('-i', '--income_file', default='income.csv',
#                         required=True, help='path where income CSV file will ' \
#                         'be written to')
#     parser.add_argument('-x', '--expenses_file', default='expenses.csv',
#                         required=True, help='path where expenses CSV file ' \
#                         'will be written to')
#     parser.add_argument('-w', '--write_mode', default='a', required=True,
#                         help='write mode for both the income and expenses CSV')

def main():
    parser = argparse.ArgumentParser(description='Organize raw finances.')
    parser.add_argument('files', nargs='+',
                        help='CSV file(s) containing finances')
    parser.add_argument('-d', '--debug', action='store_true', help='enable ' \
                        'debug output')
    parser.add_argument('-e', '--exceptions', help='a CSV of newline ' \
                        'separated descriptions that if found will get ' \
                        'removed from the data')
    parser.add_argument('-i', '--income_file', default='income.csv',
                        help='path where income CSV file will be written to, ' \
                        ' default is "income.csv"')
    parser.add_argument('-x', '--expenses_file', default='expenses.csv',
                        help='path where expenses CSV file will be written ' \
                        'to, default is "expenses.csv"')
    parser.add_argument('-w', '--write_mode', default='a',help='write mode ' \
                        'for both the income and expenses CSV, default is "a"')

    args = parser.parse_args()
    print(args)
    global debug
    debug = args.debug

    income, expenses = organize_data(args.exceptions, args.files)

    write_file(income, args.income_file, args.write_mode)
    write_file(expenses, args.expenses_file, args.write_mode)

if __name__ == "__main__":
    main()
