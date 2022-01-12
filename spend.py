'''preprocesses bank csv exports for spend spreadsheet fom local folder'''

import argparse
import os
from datetime import datetime
import numpy as np
import pandas as pd

# TODO:
# remove the giant tabs in amex us line items
# train a model on the categories
# find a way to differentiate TD csvs
# decide if GCP is overkill
# paste it directly into Sheets using API
# decide if savings, investing should connect, currently does not

INPUT_DATE_FORMAT = '%m/%d/%Y'
INPUT_FOLDER = '/Users/allengour/Desktop'
ALLEN_FOLDER = 'allen'
JESSICA_FOLDER = 'jessica'
OUTPUT_FOLDER = INPUT_FOLDER
COLUMNS = [
    'date', 'who', 'card', 'currency', 'item', 'debit', 'credit', 'category'
]


def get_files():
  '''Assembles list of file tuples for data preprocessing

  Returns:
    dict, of list of tuples; key:bank, val:[(str filepath, str who)...]
  '''
  files = [(f'{INPUT_FOLDER}/{ALLEN_FOLDER}/{file}', 'allen')
           for file in os.listdir(f'{INPUT_FOLDER}/{ALLEN_FOLDER}')]
  files += [(f'{INPUT_FOLDER}/{JESSICA_FOLDER}/{file}', 'jessica')
            for file in os.listdir(f'{INPUT_FOLDER}/{JESSICA_FOLDER}')]

  cards = {
      'amexus': [],
      'amexca': [],
      'visaca': [],
      'chequs': [],
      'cheqca': [],
  }

  for full_file in files:
    file = full_file[0]
    if file.lower()[-4:] == '.csv':
      if 'Chase' in file:
        cards['chequs'].append(full_file)
      elif 'ofx' in file:
        cards['amexca'].append(full_file)
      elif 'accountactivity' in file:
        cards['visaca'].append(full_file)
      elif 'activity' in file:
        cards['amexus'].append(full_file)
      elif 'td' in file:  # need to manually rename debit csvs
        cards['cheqca'].append(full_file)

  return cards


def preprocess(month, cards):
  '''Preprocesses CSVs from each bank into one DataFrame with consistent format

  Args:
    month: int, month number to process
    cards: dict, of list of tuples; key:bank, val:[(str filepath, str who)...]

  Returns:
    DataFrame, preprocessed data
  '''
  processed = []

  print('--> processing amex ca')
  for file in cards['amexca']:
    df = pd.read_csv(file[0], header=None)
    df = df[[0, 2, 3]]  # drop reference # and any comments
    df.columns = ['date', 'amount', 'item']
    df['debit'] = np.where(df['amount'] < 0, abs(df['amount']), np.nan)
    df['credit'] = np.where(df['amount'] >= 0, df['amount'], np.nan)
    df['who'] = file[1]
    df['card'] = 'amex ca'
    df['currency'] = 'CAD'
    df = df.reindex(columns=COLUMNS, fill_value=np.nan)
    processed.append(df)

  print('--> processing amex us')
  for file in cards['amexus']:
    df = pd.read_csv(file[0], header=0)  # drop header column
    df.columns = ['date', 'item', 'amount']
    df['debit'] = np.where(df['amount'] < 0, abs(df['amount']), np.nan)
    df['credit'] = np.where(df['amount'] >= 0, df['amount'], np.nan)
    df['who'] = file[1]
    df['card'] = 'amex us'
    df['currency'] = 'USD'
    df = df.reindex(columns=COLUMNS, fill_value=np.nan)
    processed.append(df)

  print('--> processing visa ca')
  for file in cards['visaca']:
    df = pd.read_csv(file[0], header=None)
    df = df.drop(labels=4, axis=1)  # drop balance tab
    df.columns = ['date', 'item', 'credit', 'debit']
    df['who'] = file[1]
    df['card'] = 'visa ca'
    df['currency'] = 'CAD'
    df = df.reindex(columns=COLUMNS, fill_value=np.nan)
    processed.append(df)

  print('--> processing cheq ca')
  for file in cards['cheqca']:
    df = pd.read_csv(file[0], header=None)
    df = df.drop(labels=4, axis=1)  # drop balance tab
    df.columns = ['date', 'item', 'credit', 'debit']
    df['who'] = file[1]
    df['card'] = 'cheq ca'
    df['currency'] = 'CAD'
    df = df.reindex(columns=COLUMNS, fill_value=np.nan)
    processed.append(df)

  print('--> processing cheq us')
  for file in cards['chequs']:
    # force index col to not use first col, need for some reason
    df = pd.read_csv(file[0], header=0, index_col=False)
    # only keep CR/DR, date, desc, amount
    df['debit'] = np.where(df['Details'] == 'CREDIT', df['Amount'], np.nan)
    df['credit'] = np.where(df['Details'] == 'DEBIT', abs(df['Amount']), np.nan)
    df = df[['Posting Date', 'Description', 'debit', 'credit']]
    df.columns = ['date', 'item', 'debit', 'credit']
    df['who'] = file[1]
    df['card'] = 'cheq us'
    df['currency'] = 'USD'
    df = df.reindex(columns=COLUMNS, fill_value=np.nan)
    processed.append(df)

  df = pd.concat(processed)
  # TODO: make this an exclusion list type thing
  df = df.loc[~df['item'].str.contains('THANK YOU')]
  check_date = lambda d: d if datetime.strptime(d, INPUT_DATE_FORMAT
                                               ).month == month else False
  df['date'] = df['date'].apply(check_date)
  df = df.loc[df['date'] != False]
  df.sort_values(['date', 'who', 'card', 'item'], inplace=True)
  print('-> done')

  return df


def main(month):
  '''main entry point'''
  print('-> starting spend:')
  cards = get_files()
  processed_df = preprocess(month, cards)
  # write to csv
  processed_df.to_csv(f'{OUTPUT_FOLDER}/spend.csv', header=None, index=None)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='preprocess spend')
  parser.add_argument('month', type=int, help='month')
  # optional to specify different input/allen/jessica/output folders
  parser.add_argument('--input_folder', type=str, help='input folder')
  parser.add_argument('--allen_folder', type=str, help='allen folder')
  parser.add_argument('--jessica_folder', type=str, help='jessica folder')
  parser.add_argument('--output_folder', type=str, help='output folder')
  args = parser.parse_args()
  # set folders, if provided
  if args.input_folder:
    INPUT_FOLDER = args.input_folder
  if args.allen_folder:
    ALLEN_FOLDER = args.allen_folder
  if args.jessica_folder:
    JESSICA_FOLDER = args.jessica_folder
  if args.output_folder:
    OUTPUT_FOLDER = args.output_folder
  main(args.month)
