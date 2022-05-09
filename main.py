import argparse

from organize import categorize_data, create_data_frame, get_json_from_file, separate_expenses_and_income, write_final_df_to_file


def get_args():
    parser = argparse.ArgumentParser(description='Organize raw finances')
    parser.add_argument('file', help='JSON formatted file containing '
                        'names of files with expenses and income to organize')
    return parser.parse_args()

def main():
    args = get_args()
    configs = get_json_from_file(args.file)
    dataframes = []

    for account in configs['finance_data']:
        dataframes.append(create_data_frame(configs['finance_data'][account]))
    expenses, income = separate_expenses_and_income(dataframes)
    print(f'Expenses:\n{expenses}\nIncome:\n{income}')

    organized_income = categorize_data(income, 'income')
    organized_expenses = categorize_data(expenses, 'expenses')

    if not organized_income.empty:
        write_final_df_to_file(organized_income, path=configs['out_files']['income_file'])
    if not organized_expenses.empty:
        write_final_df_to_file(organized_expenses, path=configs['out_files']['expenses_file'])

if __name__ == '__main__':
    main()