'''Main entry point and orchestration of spend flow'''

import preprocess
import sheets

import argparse

# TODO:
# remove the giant tabs in amex us & chase line items
# train a model on the categories
# decide if GCP is overkill
# decide if savings, investing should connect, currently does not


def main(month):
  '''main entry point

  Args:
    month: int, the monthnum for which transactions are being processed
  '''
  print('-> starting spend:')
  # preprocess
  cards = preprocess.get_files()
  transactions = preprocess.preprocess(month, cards, save=False)
  print(f'-> done: {len(transactions)} rows preprocessed')
  # insert into sheet
  # sheets.insert(transactions)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='spend: preprocess & load')
  parser.add_argument('month', type=int, help='month')
  args = parser.parse_args()
  main(args.month)
