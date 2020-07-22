import argparse


def main():
    parser = argparse.ArgumentParser(description='Visualize organzied ' \
                                     'finances.')
    parser.add_argument('-d', '--debug', action='store_true', help='enable ' \
                        'debug output')
    parser.add_argument('-i', '--income_file', default='income.csv',
                        help='path where income CSV file will be written to, ' \
                        ' default is "income.csv"')
    parser.add_argument('-x', '--expenses_file', default='expenses.csv',
                        help='path where expenses CSV file will be written ' \
                        'to, default is "expenses.csv"')

    args = parser.parse_args()
    global DEBUG
    DEBUG = args.debug

if __name__ == "__main__":
    main()
