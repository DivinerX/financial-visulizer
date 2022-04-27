import argparse

from new_organize import create_data_frame, get_json_from_file


def get_args():
    parser = argparse.ArgumentParser(description='Organize raw finances')
    parser.add_argument('file', help='JSON formatted file containing '
                        'names of files with expenses and income to organize')
    return parser.parse_args()

def main():
    args = get_args()
    configs = get_json_from_file(args.file)
    dataframes = []
    for account in configs:
        dataframes.append(create_data_frame(account, configs[account]))

if __name__ == '__main__':
    main()