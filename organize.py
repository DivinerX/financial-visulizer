import argparse
import numpy as np
import pandas as pd


def organize_files(*args):
    # Read and concatenate files into single dataframe.
    raw_df = pd.concat(map(pd.read_csv, *args))
    trimmed_df = pd.DataFrame(raw_df, columns = ['Posting Date', 'Amount'])
    if debug:
        # Can't use a starred expression in fstrings so I used format this time.
        print('Files given: {}'.format(*args))
        print(f'Raw dataframe:\n{raw_df}\n')
        print(f'Trimmed dataframe:\n{trimmed_df}\n')
    income = organize_income(trimmed_df)
    expenses = organize_expenses(trimmed_df)

def organize_income(df):
    income = df.copy()
    # Rename columns.
    income = income.drop(income[income.Amount < 0].index)
    income.columns = ['Date', 'Income']
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
    expenses.columns = ['Date', 'Expense']
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

def main():
    parser = argparse.ArgumentParser(description='Organize raw finances.')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable \
                                                                    debug \
                                                                    output.')
    parser.add_argument('-f', '--files', nargs='*', required=True,
                        help='CSV file(s) containing finances.')
    args = parser.parse_args()
    global debug
    debug = args.debug

    organize_files(args.files)

if __name__ == "__main__":
    main()
