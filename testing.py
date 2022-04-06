"""Testing sandbox file"""

import preprocess

MONTH = 3  # change this as needed


def main(month):
  """Main entry point.

  Args:
    month: int, the monthnum for which transactions are being processed.
  """
  print('-> starting spend:')
  # preprocess
  cards = preprocess.get_files()
  transactions = preprocess.preprocess(month, cards, save=True)
  print(f'-> {len(transactions)} rows preprocessed')


if __name__ == '__main__':
  main(MONTH)
