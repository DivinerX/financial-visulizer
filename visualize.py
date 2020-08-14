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

def months_bar_graph(title, file, monthly_sums):
    logging.debug('Entering months_bar_graph')
    line_chart = pygal.Bar()
    line_chart.legend_at_bottom=True
    # line_chart.legend_at_bottom_columns=len(month_frames)
    line_chart.title = title

    for sum in monthly_sums:
        line_chart.add(sum[0], sum[1])
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
            line_chart.add(item[0], item[1])
    else:
        for name, sum in monthly_sums.items():
            line_chart.add(name, sum)
    line_chart.render_to_file(GRAPHS_DIR + file)

def middle_month_line_chart(i_df, e_df, title, file):
    line_chart = pygal.Line()
    line_chart.title = title
    # line_chart.x_labels = ['map(str, range(2002, 2013))']

    sliced_i_df = date_range_slice(i_df, '2020-05-12', '2020-06-12')
    sliced_e_df = date_range_slice(e_df, '2020-05-12', '2020-06-12')
    i_sum = sliced_i_df['Income'].sum().round(2)
    e_sum = sliced_e_df['Expense'].sum().round(2)
    line_chart.add('May-Jun', i_sum + e_sum)
    line_chart.render_to_file(GRAPHS_DIR + file)


def date_range_slice(df, start, end):
    logging.debug('Entering date_range_slice')
    logging.debug(f'Start: {start}, End: {end}')
    logging.debug(f'Orginal dataframe:\n{df}\n')
    mask = (df['Date'] >= start) & (df['Date'] <= end)
    sliced_df = df.loc[mask]
    logging.debug(f'Sliced dataframe:\n{sliced_df}\n')
    return sliced_df

def split_months_into_frames(df):
    logging.debug('Entering split_months_into_frames')
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

def calculate_monthly_sums(month_frames, total_monthly_sums):
    # Monthly sums unique to the dataframe passed in, whether income or expense.
    monthly_sums = []
    for month in month_frames:
        month_sum = month.iloc[:, 1].sum().round(2)
        # Reset index for each month frame so I can access index 0 on each.
        month = month.reset_index()
        # Make each bar name in "Month Year" format.
        bar_name = month['Date'].dt.month_name()[0] + ' ' + str(month['Date'].dt.year[0])
        # If the month and year already exist then add it to the existing
        # dict entry.
        if bar_name in total_monthly_sums:
            new_sum = (total_monthly_sums[bar_name] + month_sum).round(2)
            total_monthly_sums[bar_name] = new_sum
        # If the month and year don't exist, create a new dict entry for it.
        else:
            total_monthly_sums[bar_name] = month_sum
        monthly_sums.append((bar_name, month_sum))
    return monthly_sums

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
        i_df = pd.read_csv(args.income)
        e_df = pd.read_csv(args.expenses)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)

    if args.debug:
        format = f'[{HEADER}%(asctime)s{RESET} - {OKGREEN}%(levelname)s {RESET}] %(message)s'
        logging.basicConfig(level=logging.DEBUG,
                            format=format, datefmt=f'%H:%M:%S')

    if args.start_date and args.end_date:
        title = args.start_date + ' - ' + args.end_date
        pie_chart_date_range(e_df, f'Expenses {title}', args.start_date,
                             args.end_date, 'expenses_date_range.svg')
        pie_chart_date_range(i_df, f'Income {title}', args.start_date,
                             args.end_date, 'income_date_range.svg')

    # Monthly total for income and expenses combined. Gets filled in by the
    # calculate_monthly_sums() method.
    total_monthly_sums = {}
    i_month_frames = split_months_into_frames(i_df)
    e_month_frames = split_months_into_frames(e_df)
    i_monthly_sums = calculate_monthly_sums(i_month_frames, total_monthly_sums)
    e_monthly_sums = calculate_monthly_sums(e_month_frames, total_monthly_sums)

    total_categories_pie_chart(e_df, 'Expenses Categories Total',
                               'expense_categories_total.svg')
    total_categories_pie_chart(i_df, 'Income Categories Total',
                               'income_categories_total.svg')
    total_bar_graph(i_df, e_df,
                    'Total Income, Expenses, and Savings', 'bar_graph.svg')

    months_bar_graph('Monthly Income', 'monthly_income.svg', i_monthly_sums)
    months_bar_graph('Monthly Expenses', 'monthly_expenses.svg', e_monthly_sums)
    combined_months_bar_graph('Combined Monthly', 'combined_months.svg',
                              total_monthly_sums)
    middle_month_line_chart(i_df, e_df, 'Middle month',
                            'middle_month.svg')

if __name__ == "__main__":
    main()
