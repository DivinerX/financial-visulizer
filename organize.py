import argparse
import numpy as np
import pandas as pd


def organize_files(*args):
    # Read and concatenate files into single dataframe.
    df = pd.concat(map(pd.read_csv, *args))
    if debug:
        # Can't use a starred expression in fstrings so I used format this time.
        print('Files given: {}'.format(*args))
        print(f'Combined dataframe:\n{df}')
    organize_expenses(df)

def organize_expenses(expense_dataframe):
    df = pd.DataFrame(expense_dataframe, columns = ['Posting Date', 'Amount'])
    # Rename columns.
    df.columns = ['Date', 'Expense']
    # Convert dates to format that pandas can work with.
    df['Date'] = pd.to_datetime(df['Date'])
    # Make the Date column the new index.
    df.index = df['Date']
    del df['Date']
    df = df.sort_index()

    # Remove all rows with positive numbers.
    df = df.drop(df[df.Expense > 0].index)
    # Convert all negatives prices to positive.
    df['Expense'] = df['Expense'].abs()
    if debug:
        print(f'Organized expenses:\n{df}')

def organize_income(income_dataframe):
    # TODO: Implement complementary income parser.
    pass

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
