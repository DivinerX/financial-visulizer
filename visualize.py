import argparse
from calendar import isleap
from datetime import datetime
import logging
import os
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pygal
from pygal.style import Style

GRAPHS_DIR = 'graphs/'
HEADER = '\033[95m'
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
# Same as the default pygal style except with a white background.
PJ_STYLE = Style(
    background = '#FFF',
    plot_background = 'rgba(255, 255, 255, 1)',
    foreground = 'rgba(0, 0, 0, .87)',
    foreground_strong = 'rgba(0, 0, 0, 1)',
    foreground_subtle = 'rgba(0, 0, 0, .54)',
    opacity = '.7',
    opacity_hover = '.8',
    transition = '250ms ease-in',
    colors = ('#F44336', '#3F51B5', '#009688', '#FFC107', '#FF5722', '#9C27B0',
              '#03A9F4', '#8BC34A', '#FF9800', '#E91E63', '#2196F3', '#4CAF50',
              '#FFEB3B', '#673AB7', '#00BCD4', '#CDDC39', '#9E9E9E', '#607D8B')
)


def pie_chart_date_range(df, title, start, end, file):
    logging.info('Entering pie_chart_date_range')
    logging.debug(f'Start: {start}, End: {end}')
    logging.debug(f'Orginal dataframe:\n{df}\n')
    pie_chart = pygal.Pie(style=PJ_STYLE)
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
    logging.info(f'Generating report {GRAPHS_DIR + file}\n')
    pie_chart.render_to_file(GRAPHS_DIR + file)
    return GRAPHS_DIR + file

def total_categories_pie_chart(df, title, file):
    logging.info('Entering total_categories_pie_chart')
    pie_chart = pygal.Pie(style=PJ_STYLE)
    pie_chart.title = title
    # Expense or Income.
    type = df.columns[1]

    unique_categories = pd.unique(df['Category'])
    for category in unique_categories:
        # Sum all transactions of the current category.
        sum = abs(df.loc[df['Category'] == category][type].sum().round(2))
        logging.debug(f'Category: {category}, Sum: {sum}')
        pie_chart.add(category, sum)
    logging.info(f'Generating report {GRAPHS_DIR + file}\n')
    pie_chart.render_to_file(GRAPHS_DIR + file)
    return GRAPHS_DIR + file

def total_bar_graph(i_df, e_df, title, file):
    logging.info('Entering total_bar_graph')
    line_chart = pygal.Bar(style=PJ_STYLE)
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
    logging.info(f'Generating report {GRAPHS_DIR + file}\n')
    line_chart.render_to_file(GRAPHS_DIR + file)
    return GRAPHS_DIR + file

def months_bar_graph(monthly_sums, title, file):
    logging.info('Entering months_bar_graph')
    line_chart = pygal.Bar(style=PJ_STYLE)
    line_chart.legend_at_bottom=True
    # line_chart.legend_at_bottom_columns=len(month_frames)
    line_chart.title = title

    for sum in monthly_sums:
        line_chart.add(sum[0], sum[1])

    logging.info(f'Generating report {GRAPHS_DIR + file}\n')
    line_chart.render_to_file(GRAPHS_DIR + file)
    return GRAPHS_DIR + file

def combined_months_bar_graph(sum_df, title, file):
    logging.info('Entering combined_months_bar_graph')
    line_chart = pygal.Bar(style=PJ_STYLE)
    line_chart.legend_at_bottom=True
    line_chart.title = title
    dates = sum_df['Date'].dt.strftime('%B %Y').tail(15)
    entries = len(sum_df.index)

    # TODO: test what happens when no entries are passed to this method or others
    if entries < 15 and entries >= 0:
        for i in range(entries):
            line_chart.add(dates[i], sum_df.iloc[i]['Sum'])
    elif entries >= 15:
        # Iterate through the last fifteen rows of the dataframe if possible.
        for i in range((entries-15), entries, 1):
            line_chart.add(dates[i], sum_df.iloc[i]['Sum'])
    else:
        print(f'Invalid number "{entries}" passed to combined_months_bar_graph.')
        sys.exit(8)

    logging.info(f'Generating report {GRAPHS_DIR + file}\n')
    line_chart.render_to_file(GRAPHS_DIR + file)
    return GRAPHS_DIR + file

def middle_month_line_chart(sum_df, title, file):
    logging.info('Entering middle_month_line_chart')
    line_chart = pygal.Line(style=PJ_STYLE, x_label_rotation=45,
                            show_legend=False)
    line_chart.title = title
    line_chart.x_labels = sum_df['Date'].dt.strftime('%b %Y').tail(15)

    line_chart.add('', sum_df['Mid-sum'].tail(15))
    logging.info(f'Generating report {GRAPHS_DIR + file}\n')
    line_chart.render_to_file(GRAPHS_DIR + file)
    return GRAPHS_DIR + file

def category_over_time_chart():
    pass

def date_range_slice(df, start, end):
    logging.debug(f'date_range_slice - Start: {start}, End: {end}')
    mask = (df['Date'] >= start) & (df['Date'] <= end)
    sliced_df = df.loc[mask]
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
        logging.debug(f'Sum: {sum}, Mid-sum: {mid_sum}')
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

# Taken from https://stackoverflow.com/questions/16870663/how-do-i-validate-a-date-string-format-in-python#answer-37045601
def validate_date(date):
    try:
        # If only strptime is called leading zeroes don't get checked.
        if date != datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d'):
            # This is a catchall since some error cases throw ValueErrors and
            # some don't. This way all error cases should return the same thing.
            raise ValueError
    except ValueError:
        print(f'Incorrect date format, "{date}" should be in ' \
              'YYYY-MM-DD format.')
        sys.exit(7)

def create_web_page(graphs):
    logging.info('Entering create_web_page')
    svgs = ''
    index = 1
    box_shadow = 'box-shadow: 0 1px 2px 0 rgba(60,64,67,.3),0 1px 3px 1px rgba(60,64,67,.15);'
    for graph in graphs:
        # If last graph is an odd number then center it on the page instead
        # of making go left or right.
        if index == len(graphs) and (index % 2) != 0:
            svgs += '\n    <div style="width:48%; display:block; margin-left: auto; margin-right: auto;">'
        # Put graph on right side of page if it's an even number.
        elif (index % 2) == 0:
            svgs += '\n    <div style="width:48%; display:block; float:right; margin-left: 0.15em">'
        # Number isn't even so put it on left side of page.
        else:
            svgs += '\n    <div style="width:48%; display:block; float:left; margin-right: 0.15em">'
        svgs += f'\n        <object type="image/svg+xml" data="{graph}" style="{box_shadow}"></object>'
        svgs += '\n    </div>\n'
        index += 1

    html = f'''<!DOCTYPE html>
<html lang="en-us">

<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<meta http-equiv="X-UA-Compatible" content="ie=edge">
	<title>Peter Brunner</title>
</head>

<body style="background: bisque;">
    <div style="display: block; margin-left: auto; margin-right: auto; width: 90%;">
        {svgs}
    </div>
</body>
    '''

    with open('index.html', 'w') as f:
        logging.info('Writing HTML to index.html')
        f.write(html)

def create_graphs(i_df, e_df, start_date, end_date):
    graphs = []

    if start_date and end_date:
        validate_date(start_date)
        validate_date(end_date)
        title = start_date + ' : ' + end_date
        graphs.append(pie_chart_date_range(e_df, f'Expenses {title}',
                                           start_date, end_date,
                                           'expenses_date_range.svg'))
        graphs.append(pie_chart_date_range(i_df, f'Income {title}',
                                           start_date, end_date,
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
    return graphs

def get_args():
    parser = argparse.ArgumentParser(description='Visualize organzied ' \
                                     'finances.')
    parser.add_argument('-i', '--info', action='store_true', help='enable ' \
                        'debug output')
    parser.add_argument('-d', '--debug', action='store_true', help='enable ' \
                        'more detailed debug output')
    parser.add_argument('income', help='CSV containing income, this must ' \
                        'be given before expenses')
    parser.add_argument('expenses', help='CSV containing expenses')
    parser.add_argument('-s', '--start_date', help='date in YYYY-MM-DD format ' \
                        'for pie chart to start from')
    parser.add_argument('-e', '--end_date', help='date in YYYY-MM-DD format ' \
                        'for pie chart to end on')
    parser.add_argument('-c', '--category', help='generate monthly sums only for ' \
                        'for the given category; categories are found in categories.py')

    return parser.parse_args()

def main():
    args = get_args()

    if not os.path.isdir('graphs'):
        Path('graphs').mkdir(exist_ok=True)

    try:
        i_df = pd.read_csv(args.income)
        e_df = pd.read_csv(args.expenses)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)
    except pd.errors.EmptyDataError as e:
        print(e)
        sys.exit(2)

    if i_df.empty:
        print('Income CSV has no data.')
        sys.exit(3)
    if e_df.empty:
        print('Expenses CSV has no data.')
        sys.exit(4)

    format = f'[{HEADER}%(asctime)s{RESET} - {OKGREEN}%(levelname)s {RESET}] %(message)s'
    if args.info:
        logging.basicConfig(level=logging.INFO,
                            format=format, datefmt=f'%H:%M:%S')
    if args.debug:
        logging.basicConfig(level=logging.DEBUG,
                            format=format, datefmt=f'%H:%M:%S')

    # Ensure the income df has no expenses and the expenses df has no income.
    if not i_df[i_df.select_dtypes(include=[np.number]).le(0).all(1)].empty:
        print('Income dataframe contains expense(s).')
        sys.exit(5)
    if not e_df[e_df.select_dtypes(include=[np.number]).ge(0).all(1)].empty:
        print('Expenses dataframe contains income.')
        sys.exit(6)

    graphs = create_graphs(i_df, e_df, args.start_date, args.end_date)

    create_web_page(graphs)

if __name__ == "__main__":
    main()
