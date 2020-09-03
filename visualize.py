import argparse
from calendar import isleap
import logging
import os
from pathlib import Path
import sys

import pandas as pd
import pygal

GRAPHS_DIR = 'graphs/'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RESET = '\x1b[0m'
MONTHS = {'January': '01', 'February': '02', 'March': '03', 'April': '04',
          'May': '05', 'June': '06', 'July': '07', 'August': '08',
          'September': '09', 'October': '10', 'November': '11',
          'December': '12'}


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
    return GRAPHS_DIR + file

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
    return GRAPHS_DIR + file

def total_bar_graph(i_df, e_df, title, file):
    logging.debug('Entering total_bar_graph')
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
    return GRAPHS_DIR + file

def months_bar_graph(monthly_sums, title, file):
    logging.debug('Entering months_bar_graph')
    line_chart = pygal.Bar()
    line_chart.legend_at_bottom=True
    # line_chart.legend_at_bottom_columns=len(month_frames)
    line_chart.title = title

    for sum in monthly_sums:
        line_chart.add(sum[0], sum[1])
    line_chart.render_to_file(GRAPHS_DIR + file)
    return GRAPHS_DIR + file

def combined_months_bar_graph(sum_df, title, file):
    logging.debug('Entering combined_months_bar_graph')
    line_chart = pygal.Bar()
    line_chart.legend_at_bottom=True
    line_chart.title = title
    dates = sum_df['Date'].dt.strftime('%B %Y').tail(15)
    entries = len(sum_df.index)

    # Iterate through the last fifteen rows of the dataframe.
    for i in range((entries-15), entries, 1):
        line_chart.add(dates[i], sum_df.iloc[i]['Sum'])
    line_chart.render_to_file(GRAPHS_DIR + file)
    return GRAPHS_DIR + file

def middle_month_line_chart(sum_df, title, file):
    logging.debug('Entering middle_month_line_chart')
    line_chart = pygal.Line(x_label_rotation=45, show_legend=False)
    line_chart.title = title
    line_chart.x_labels = sum_df['Date'].dt.strftime('%b %Y').tail(15)

    line_chart.add('', sum_df['Mid-sum'].tail(15))
    line_chart.render_to_file(GRAPHS_DIR + file)
    return GRAPHS_DIR + file

def date_range_slice(df, start, end):
    logging.debug('Entering date_range_slice')
    logging.debug(f'Start: {start}, End: {end}')
    logging.debug(f'Orginal dataframe:\n{df}\n')
    mask = (df['Date'] >= start) & (df['Date'] <= end)
    sliced_df = df.loc[mask]
    logging.debug(f'Sliced dataframe:\n{sliced_df}\n')
    return sliced_df

def sums(df, sum_df):
    # Get list of all unique year/month combinations in dataframe (YYYY-MM).
    month_years = df['Date'].dt.strftime('%Y-%m').unique().tolist()
    # List of individual sums, it either be expense or income sums.
    sum_list = []
    for month_year in month_years:
        month = month_year.split('-')[1]
        year = month_year.split('-')[0]
        prev_month = get_prev_month(month, year)
        last_day = last_day_of_month(month, year)

        sum = date_range_slice(df, f'{month_year}-1', f'{month_year}-{last_day}').iloc[:, 1].sum().round(2)
        mid_sum = date_range_slice(df, f'{prev_month}-12', f'{month_year}-12').iloc[:, 1].sum().round(2)
        sum_list.append((month_year, sum))
        sum_df = sum_df.append({'Date': month_year + '-1', 'Sum': sum, 'Mid-sum': mid_sum}, ignore_index=True)
    return sum_df, sum_list

def last_day_of_month(month, year):
    if month == '02':
        # Check for leap year.
        if isleap(int(year)):
            return '29'
        else:
            return '28'
    elif month == '04' or month == '06' or month == '09' or month == '11':
        return '30'
    # If no other special conditions caught then the month must have 31 days.
    return '31'

def get_prev_month(month, year):
    # If month is January then return decremented year and December as month.
    if month == '01':
        return (str(int(year) - 1)) + '-' + '12'
    # Don't add leading 0 to prev month if current month is 11 or 12.
    elif month == '11' or month == '12':
        return year + '-' + (str(int(month) - 1))
    # Add leading 0 to month so it's compatible with pandas YYYY-MM-DD format.
    else:
        return year + '-' + ('0' + str(int(month) - 1))

def create_web_page(graphs):
    logging.debug('Entering create_web_page')
    svgs = ''
    for graph in graphs:
        with open(graph, 'r') as f:
            logging.debug(f'Reading contents of "{graph}"')
            svgs += f.read() + '\n'

    html = f'''
<!DOCTYPE html>
<html lang="en-us">

<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<meta http-equiv="X-UA-Compatible" content="ie=edge">
	<title>Peter Brunner</title>
</head>

<body>
    <h1>Test web page</h1>
    {svgs}
</body>
    '''

    with open('index.html', 'w') as f:
        f.write(html)

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
    graphs = []

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
        title = args.start_date + ' : ' + args.end_date
        graphs.append(pie_chart_date_range(e_df, f'Expenses {title}',
                                           args.start_date, args.end_date,
                                           'expenses_date_range.svg'))
        graphs.append(pie_chart_date_range(i_df, f'Income {title}',
                                           args.start_date, args.end_date,
                                           'income_date_range.svg'))

    # Convert the 'Date' category to pandas datetime format.
    # Invalid parsing will be set as NaT (missing value).
    i_df['Date'] = pd.to_datetime(i_df['Date'], errors='coerce')
    e_df['Date'] = pd.to_datetime(e_df['Date'], errors='coerce')

    # Mid-sum is the sum of the second half of the previous month + the first
    # half of the current month.
    sum_df = pd.DataFrame(columns=['Date', 'Sum', 'Mid-sum'])
    sum_df, i_sums = sums(i_df, sum_df)
    sum_df, e_sums = sums(e_df, sum_df)

    sum_df['Date'] = pd.to_datetime(sum_df['Date'], errors='coerce')
    # Combine sums for duplicate year/month combinations and sort.
    sum_df = sum_df.groupby('Date', as_index=False).sum().round(2)

    graphs.append(middle_month_line_chart(sum_df, 'Mid-month sums',
                                          'mid_month_sums.svg'))

    graphs.append(total_categories_pie_chart(e_df, 'Expenses Categories Total',
                                             'expense_categories_total.svg'))
    graphs.append(total_categories_pie_chart(i_df, 'Income Categories Total',
                                             'income_categories_total.svg'))
    graphs.append(total_bar_graph(i_df, e_df,
                                  'Total Income, Expenses, and Savings',
                                  'bar_graph.svg'))

    graphs.append(months_bar_graph(i_sums, 'Monthly Income',
                                   'monthly_income.svg'))
    graphs.append(months_bar_graph(e_sums, 'Monthly Expenses',
                                   'monthly_expenses.svg'))
    graphs.append(combined_months_bar_graph(sum_df, 'Combined Monthly',
                                            'combined_months.svg'))

    create_web_page(graphs)

if __name__ == "__main__":
    main()
