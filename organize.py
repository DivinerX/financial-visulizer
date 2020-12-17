import argparse
import csv
import os
import sys

import numpy as np
import pandas.errors
import pandas as pd

from categories import E_CATEGORIES, I_CATEGORIES

# Terminal color codes.
BOLD = '\033[1m'
RESET = '\x1b[0m'


def organize_data(exceptions_file, *args):
    raw_df = read_files(*args)

    if DEBUG:
        # Can't use a starred expression in fstrings so I used format this time.
        print('Files given: {}'.format(*args))
        print(f'Raw dataframe:\n{raw_df}\n')

    filtered_df = remove_exceptions(exceptions_file, raw_df)
    trimmed_df = pd.DataFrame(filtered_df, columns = ['Posting Date', 'Amount',
                              'Extended Description'])
    if DEBUG:
        print(f'Trimmed dataframe:\n{trimmed_df}\n')

    income = organize_income(trimmed_df)
    expenses = organize_expenses(trimmed_df)

    # Get the user to fill out 'Category', 'To/From', and 'Description' columns.
    income = fill_remaining_columns(income, I_CATEGORIES)
    expenses = fill_remaining_columns(expenses, E_CATEGORIES)

    if DEBUG:
        print(f'Final income dataframe:\n{income}\n')
        print(f'Final expenses dataframe:\n{expenses}\n')

    return income, expenses

def read_files(files):
    # Read and concatenate files into single dataframe.
    dataframes = []
    for file in files:
        try:
            df = pd.read_csv(file)
            if {'Posting Date', 'Amount', 'Extended Description'}.issubset(df.columns):
                dataframes.append(df)
            else:
                print(f'Skipping file {BOLD}{file}{RESET}, missing required ' \
                      'column(s)')
                continue
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)
        except pandas.errors.EmptyDataError as e:
            print(f'Skipping empty file {BOLD}{file}{RESET}')

    if not dataframes:
        print('Exiting, no usable files')
        sys.exit(2)

    return pd.concat(dataframes)

def remove_exceptions(exceptions_file, raw_df):
    exceptions = []
    try:
        with open(exceptions_file, newline='') as f:
            lines = csv.reader(f)
            iterlines = iter(lines)
            for line in iterlines:
                # Get the exception from each line.
                exceptions.append(line[0].strip())
    except (TypeError, FileNotFoundError):
        if DEBUG:
            print(f'No exceptions file provided.\n')
        return raw_df

    if DEBUG:
        print(f'Exceptions: {exceptions}\n')

    for exception in exceptions:
        if DEBUG:
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

    if DEBUG:
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
    expenses = expenses[expenses.select_dtypes(include=[np.number]).le(0).all(1)]

    if DEBUG:
        print(f'Organized expenses:\n{expenses}\n')
    return expenses

def fill_remaining_columns(df, category_dict):
    categories = []
    recipients = []
    descriptions = []
    for index, row in df.iterrows():
        if SKIP_INPUT:
            categories.append('NaN')
            recipients.append('NaN')
            descriptions.append('NaN')
        else:
            # Print column names.
            print([df.index.name] + df.columns.tolist())
            # Print single row of values.
            print(f'[{index}, {row[0]}, {row[1]}]')
            # Print the expense categories to choose from.
            print(category_dict)
            # Get user input to fill in the remaining columns.
            get_input(df, category_dict, categories, recipients, descriptions)
    # Add lists to the dataframe.
    df = df.assign(Category=categories)
    if list(df.columns)[0] == 'Expense':
        df = df.assign(To=recipients)
    else:
        df = df.assign(From=recipients)
    df = df.assign(Description=descriptions)

    if DEBUG:
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
    while to_from == '' or to_from.isspace():
        to_from = input('Please enter a value, any value: ')
    recipients.append(to_from)
    descriptions.append(input('(Optional) Description: '))
    # Clear the screen between each iteration.
    os.system('clear')

def good_category(category, category_dict):
    return category.isdigit() and int(category) in category_dict.keys()

def write_file(df, file_path, write_mode):
    header = None
    # Create df header to check if it already exists in file.
    columns = df.index.name
    for column in list(df.columns.values):
        columns += ',' + column

    # If the file doesn't exist, write the header.
    if not os.path.isfile(file_path):
        header=True
    else:
        # Check if write mode has 'w' and if first line of file equals header.
        with open(file_path) as f:
            first_line = f.readline().strip()
            if 'w' not in write_mode and first_line == columns:
                header=False
            else:
                header=True

    # Only write to file if the dataframe is not empty.
    if len(df.index) != 0:
        df.to_csv(path_or_buf=file_path, header=header, mode=write_mode)
        print(f'{list(df.columns)[0]} dataframe written in "{write_mode}" ' \
              f'mode to {BOLD}{file_path}{RESET}')
    else:
        print(f'{BOLD}Not{RESET} writing empty dataframe to {file_path}.')

def main():
    parser = argparse.ArgumentParser(description='Organize raw finances.')
    parser.add_argument('files', nargs='+',
                        help='CSV file(s) containing finances, required ' \
                        'columns are "Posting Date", "Amount", "Extended ' \
                        'Description"; if any one of these columns is missing' \
                        ' the whole CSV it belongs to is ignored')
    parser.add_argument('-d', '--debug', action='store_true', help='enable ' \
                        'debug output')
    parser.add_argument('-e', '--exceptions', help='a file of newline ' \
                        'separated strings that if found will get ' \
                        'removed from the data')
    parser.add_argument('-i', '--income_file', default='income.csv',
                        help='path where income CSV file will be written to, ' \
                        ' default is "income.csv"')
    parser.add_argument('-x', '--expenses_file', default='expenses.csv',
                        help='path where expenses CSV file will be written ' \
                        'to, default is "expenses.csv"')
    parser.add_argument('-w', '--write_mode', default='a',help='write mode ' \
                        'for both the income and expenses CSV, default is "a"')
    parser.add_argument('-s', '--skip_input', action='store_true',
                        help='auto fill user input step with bogus data for ' \
                        'quicker debugging')

    args = parser.parse_args()
    global DEBUG
    DEBUG = args.debug

    global SKIP_INPUT
    SKIP_INPUT = args.skip_input

    assert args.income_file != '' and not args.income_file.isspace()
    assert args.expenses_file != '' and not args.expenses_file.isspace()
    assert args.write_mode != '' and not args.write_mode.isspace()

    income, expenses = organize_data(args.exceptions, args.files)

    write_file(income, args.income_file, args.write_mode)
    write_file(expenses, args.expenses_file, args.write_mode)

if __name__ == "__main__":
    main()
