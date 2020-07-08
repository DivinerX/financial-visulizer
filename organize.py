import argparse
import numpy as np
import pandas as pd


def organize(file, debug):
    expenses = pd.read_csv(file)
    if debug:
        print(expenses)

    df = pd.DataFrame(expenses, columns = ['Posting Date', 'Amount'])
    # Rename columns.
    df.columns = ['Date', 'Price']
    # Convert dates to format that pandas can work with.
    df['Date'] = pd.to_datetime(df['Date'])
    # Make the Date column the new index.
    df.index = df['Date']
    del df['Date']
    df = df.sort_index()

    # Remove all rows with positive numbers.
    df = df.drop(df[df.Price > 0].index)
    # Convert all negatives prices to positive.
    df['Price'] = df['Price'].abs()
    if debug:
        print(df)

def main():
    parser = argparse.ArgumentParser(description='Organize raw finances.')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable \
                                                                    debug \
                                                                    output.')
    parser.add_argument('-f', '--file', help='CSV file to read from.')
    args = parser.parse_args()

    organize(args.file, args.debug)

if __name__ == "__main__":
    main()
