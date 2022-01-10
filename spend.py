'''preprocesses bank csv exports for spend spreadsheet'''

import argparse
import os
from datetime import datetime
import numpy as np
import pandas as pd

# TODO:
# remove the giant tabs in amex us line items
# train a model on the categories
# add chequing
# decide on functions

PATH = '/Users/allengour/Downloads'
INPUT_DATE_FORMAT = '%m/%d/%Y'
COLUMNS = [
  'date', 'who', 'card', 'currency', 'item', 'debit', 'credit', 'category'
]


def main(who, month):
  '''main entry point'''
  print(f'-> starting spend for {who}')
  files = os.listdir(PATH)

  cards = {
    'amexus': [],
    'amexca': [],
    'visaca': [],
    'chequs': [],
    'cheqca': [],
  }

  for file in files:
    if file[-4:] == '.csv':
      if 'ofx' in file:
        cards['amexca'].append(file)
      elif 'accountactivity' in file:
        cards['visaca'].append(file)
      elif 'activity' in file:
        cards['amexus'].append(file)
      elif 'Chase' in file:
        cards['chequs'].append(file)
      elif 'td' in file: # need to manually rename debit csvs
        cards['cheqca'].append(file)

  processed = []

  print('--> processing amex us')
  for file in cards['amexus']:
    filepath = f'{PATH}/{file}'
    df = pd.read_csv(filepath, header=0) # drop header column
    df.columns = ['date', 'item', 'credit']
    df['who'] = who
    df['card'] = 'amex us'
    df['currency'] = 'USD'
    df = df.reindex(columns=COLUMNS, fill_value=np.nan)
    processed.append(df)

  print('--> processing amex ca')
  for file in cards['amexca']:
    filepath = f'{PATH}/{file}'
    df = pd.read_csv(filepath, header=None)
    df = df[[0,2,3]] # drop reference # and any comments
    df.columns = ['date', 'credit', 'item']
    df['who'] = who
    df['card'] = 'amex ca'
    df['currency'] = 'CAD'
    df = df.reindex(columns=COLUMNS, fill_value=np.nan)
    processed.append(df)

  print('--> processing visa ca')
  for file in cards['visaca']:
    filepath = f'{PATH}/{file}'
    df = pd.read_csv(filepath, header=None)
    df = df.drop(labels=4, axis=1) # drop balance tab
    df.columns = ['date', 'item', 'credit', 'debit']
    df['who'] = who
    df['card'] = 'visa ca'
    df['currency'] = 'CAD'
    df = df.reindex(columns=COLUMNS, fill_value=np.nan)
    processed.append(df)

  print('--> processing cheq ca')
  for file in cards['cheqca']:
    filepath = f'{PATH}/{file}'
    df = pd.read_csv(filepath, header=None)
    df = df.drop(labels=4, axis=1) # drop balance tab
    df.columns = ['date', 'item', 'credit', 'debit']
    df['who'] = who
    df['card'] = 'cheq ca'
    df['currency'] = 'CAD'
    df = df.reindex(columns=COLUMNS, fill_value=np.nan)
    processed.append(df)

  df = pd.concat(processed)
  # TODO: make this an exclusion list type thing
  df = df.loc[~df['item'].str.contains('THANK YOU')]
  check_date = lambda d: d if datetime.strptime(d, INPUT_DATE_FORMAT
                          ).month == month else False
  df['date'] = df['date'].apply(check_date)
  df = df.loc[df['date'] != False]
  df.sort_values(['date', 'card', 'item'], inplace=True)
  print('-> done')

  return df


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='preprocess spend')
  parser.add_argument('who', type=str, help='transaction owner')
  parser.add_argument('month', type=int, help='month')
  args = parser.parse_args()
  final_df = main(args.who, args.month)
  final_df.to_csv(f'{PATH}/spend.csv', header=None, index=None)
