import json

import pandas as pd


def create_data_frame(configs):
    files = configs['files']
    keep_columns = configs['keep_data_from']
    # https://dev.to/balapriya/building-a-dataframe-from-multiple-files-1590
    # The [keep_columns] after read_csv reorders the header to match keep_columns.
    df = pd.concat((pd.read_csv(f, parse_dates=[keep_columns[0]])[keep_columns] for f in files), ignore_index=True)

    df.columns = ['Date', 'Description', 'Amount']

    if option_enabled(configs, 'format', 'reverse_sign', 'true'):
        df['Amount'] = df['Amount'] * -1

    if 'exceptions' in configs:
        df = remove_exceptions(configs['exceptions'], df, 'Description')

    return df

def option_enabled(configs_dict, section, option, value):
    if section in configs_dict:
        if option in configs_dict[section]:
            if configs_dict[section][option].lower() == value:
                return True
    return False

def remove_exceptions(exceptions, df, description_column):
    with open(exceptions, 'r') as f:
        for line in f:
            # Print row containing exception without the header or index column.
            print(df[df[description_column].str.contains(line.strip())].to_string(index=False, header=False))
            # Remove row containing exception.
            df = df[~df[description_column].str.contains(line.strip())]
    # Reset out of order index column and return.
    return df.reset_index(drop=True)

def separate_expenses_and_income(dataframes_list):
    df = pd.concat(dataframes_list, ignore_index=True)
    expenses, income = df[(mask:=df['Amount'] <= 0)].copy(), df[~mask].copy()
    expenses = expenses.sort_values(by='Date', ignore_index=True)
    income = income.sort_values(by='Date', ignore_index=True)
    return expenses, income

@staticmethod
def get_json_from_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)