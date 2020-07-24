import argparse
import sys

import pandas as pd
import pygal


def pie_chart_date_range(df, title):
    pie_chart = pygal.Pie()
    pie_chart.title = title
    # Sum entire column.
    print(df.iloc[:, 1].sum())
    # Sum all expense entries belonging to the "Childcare" category.
    print(df.loc[df['Category'] == 'Childcare']['Expense'].sum())
    pie_chart.add('Childcare', abs(df.loc[df['Category'] == 'Childcare']['Expense'].sum()))
    pie_chart.add('Car payment', abs(df.loc[df['Category'] == 'Car payment']['Expense'].sum()))
    pie_chart.render_to_file('pie_chart.svg')

def main():
    parser = argparse.ArgumentParser(description='Visualize organzied ' \
                                     'finances.')
    parser.add_argument('-d', '--debug', action='store_true', help='enable ' \
                        'debug output')
    parser.add_argument('income', help='CSV containing income')
    parser.add_argument('expenses', help='CSV containing expenses')

    args = parser.parse_args()
    global DEBUG
    DEBUG = args.debug

    try:
        income_df = pd.read_csv(args.income)
        expenses_df = pd.read_csv(args.expenses)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)

    pie_chart_date_range(expenses_df, 'Test title')

if __name__ == "__main__":
    main()
