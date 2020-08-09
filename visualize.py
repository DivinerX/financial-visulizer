import argparse
import logging
import os
from pathlib import Path
import sys

import pandas as pd
import pygal

GRAPHS_DIR = 'graphs/'
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RESET = '\x1b[0m'

def pie_chart_date_range(df, title, start, end, file):
    logging.debug('Entering pie_chart_date_range')
    logging.debug(f'Start: {start}, End: {end}')
    logging.debug(f'Orginal dataframe:\n{df}\n')
    pie_chart = pygal.Pie()
    pie_chart.title = title
    # Expense or Income.
    type = df.columns[1]

    sliced_df = date_range_slice(df, start, end)
    logging.debug(f'Sliced dataframe:\n{sliced_df}\n')
    unique_categories = pd.unique(sliced_df['Category'])
    for category in unique_categories:
        # Sum all transactions of the current category.
        sum = abs(sliced_df.loc[sliced_df['Category'] == category][type].sum().round(2))
        pie_chart.add(category, sum)
    pie_chart.render_to_file(GRAPHS_DIR + file)

def total_categories_pie_chart(df, title, file):
    logging.debug('Entering total_categories_pie_chart')
    pie_chart = pygal.Pie()
    pie_chart.title = title
    # Expense or Income.
    type = df.columns[1]

    unique_categories = pd.unique(df['Category'])
    for category in unique_categories:
        # Sum all transactions of the current category.
        sum = abs(df.loc[df['Category'] == category][type].sum().round(2))
        logging.debug(f'Category: {category}, Sum: {sum}')
        pie_chart.add(category, sum)
    pie_chart.render_to_file(GRAPHS_DIR + file)

def total_bar_graph(i_df, e_df, title, file):
    line_chart = pygal.Bar()
    line_chart.legend_at_bottom=True
    # Make it so the whole legend will be on just one line.
    line_chart.legend_at_bottom_columns=3
    line_chart.title = title

    # Sum entire Income/Expense column.
    i_sum = i_df.iloc[:, 1].sum().round(2)
    e_sum = e_df.iloc[:, 1].sum().round(2)
    savings = i_sum + e_sum

    line_chart.add('Total Income', i_sum)
    line_chart.add('Total Expenses', e_sum)
    line_chart.add('Total Savings', savings)
    line_chart.render_to_file(GRAPHS_DIR + file)

def months_bar_graph(df, title, file, monthly_sums):
    logging.debug('Entering months_bar_graph')
    logging.debug(f'Original dataframe: {df}')
    months = get_time(df)
    line_chart = pygal.Bar()
    line_chart.legend_at_bottom=True
    line_chart.legend_at_bottom_columns=len(months)
    line_chart.title = title

    for month in months:
        month_sum = month.iloc[:, 1].sum().round(2)
        # Reset index for each month frame so I can access index 0 on each.
        month = month.reset_index()
        # Make each bar name in "Month Year" format.
        bar_name = month['Date'].dt.month_name()[0] + ' ' + str(month['Date'].dt.year[0])
        if bar_name in monthly_sums:
            monthly_sums[bar_name] += month_sum
        else:
            monthly_sums[bar_name] = month_sum
        line_chart.add(bar_name, month_sum)
    line_chart.render_to_file(GRAPHS_DIR + file)

def combined_months_bar_graph(title, file, monthly_sums):
    line_chart = pygal.Bar()
    line_chart.legend_at_bottom=True
    # if len(monthly_sums) > 15:
    #         line_chart.legend_at_bottom_columns=15
    # else:
    #     line_chart.legend_at_bottom_columns=len(monthly_sums)
    line_chart.title = title

    if len(monthly_sums) > 15:
        # Convert dict to list so we can get the last 15 items.
        list_items = list(monthly_sums.items())
        for item in list_items[-15:]:
            print(item)
            line_chart.add(item[0], item[1])
    else:
        for name, sum in monthly_sums.items():
            print(name, sum)
            line_chart.add(name, sum)
    line_chart.render_to_file(GRAPHS_DIR + file)


def date_range_slice(df, start, end):
    logging.debug('Entering date_range_slice')
    logging.debug(f'Start: {start}, End: {end}')
    logging.debug(f'Orginal dataframe:\n{df}\n')
    mask = (df['Date'] >= start) & (df['Date'] <= end)
    sliced_df = df.loc[mask]
    logging.debug(f'Sliced dataframe:\n{sliced_df}\n')
    return sliced_df

def get_time(df):
    logging.debug('Entering get_time')
    month_frames = []
    # Convert the 'Date' category to pandas datetime format.
    # Invalid parsing will be set as NaT (missing value).
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    years = pd.unique(df['Date'].dt.year)
    for year in years:
        year_df = df[df['Date'].dt.year == year]
        months = pd.unique(year_df['Date'].dt.month)
        for month in months:
            month_df = year_df[year_df['Date'].dt.month == month]
            month_frames.append(month_df)

    logging.debug(f'Unique months: {month_frames}')
    return month_frames

def main():
    parser = argparse.ArgumentParser(description='Visualize organzied ' \
                                     'finances.')
    parser.add_argument('-d', '--debug', action='store_true', help='enable ' \
                        'debug output')
    parser.add_argument('income', help='CSV containing income')
    parser.add_argument('expenses', help='CSV containing expenses')
    parser.add_argument('-s', '--start_date', help='date in YYYY-MM-DD format ' \
                        'for pie chart to start from')
    parser.add_argument('-e', '--end_date', help='date in YYYY-MM-DD format ' \
                        'for pie chart to end on')

    args = parser.parse_args()

    if not os.path.isdir('graphs'):
        Path('graphs').mkdir(exist_ok=True)

    try:
        income_df = pd.read_csv(args.income)
        expenses_df = pd.read_csv(args.expenses)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)

    if args.debug:
        format = f'[{HEADER}%(asctime)s{RESET} - {OKGREEN}%(levelname)s {RESET}] %(message)s'
        logging.basicConfig(level=logging.DEBUG,
                            format=format, datefmt=f'%H:%M:%S')

    if args.start_date and args.end_date:
        title = args.start_date + ' - ' + args.end_date
        pie_chart_date_range(expenses_df, f'Expenses {title}', args.start_date,
                             args.end_date, 'expenses_date_range.svg')
        pie_chart_date_range(income_df, f'Income {title}', args.start_date,
                             args.end_date, 'income_date_range.svg')

    total_categories_pie_chart(expenses_df, 'Expenses Categories Total',
                               'expense_categories_total.svg')
    total_categories_pie_chart(income_df, 'Income Categories Total',
                               'income_categories_total.svg')
    total_bar_graph(income_df, expenses_df,
                    'Total Income, Expenses, and Savings', 'bar_graph.svg')
    monthly_sums = {}
    months_bar_graph(expenses_df, 'Monthly Expenses', 'monthly_expenses.svg',
                     monthly_sums)
    months_bar_graph(income_df, 'Monthly Income', 'monthly_income.svg',
                     monthly_sums)
    combined_months_bar_graph('Combined Monthly', 'combined_months.svg',
                              monthly_sums)

if __name__ == "__main__":
    main()
