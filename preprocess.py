'''preprocesses bank csv exports for spend spreadsheet fom local folder'''

import os
import yaml
import numpy as np
import pandas as pd


def get_files():
  '''Assembles list of file tuples for data preprocessing

  Returns:
    dict, of list of tuples; key:bank, val:[(str filepath, str who)...]
  '''
  with open('config.yaml', 'r', encoding='utf8') as infile:
    config = yaml.safe_load(infile)

  files = [(f'{config["input_folder"]}/{config["allen_folder"]}/{file}',
            'allen') for file in os.listdir(
                f'{config["input_folder"]}/{config["allen_folder"]}')]
  files += [(f'{config["input_folder"]}/{config["jessica_folder"]}/{file}',
             'jessica') for file in os.listdir(
                 f'{config["input_folder"]}/{config["jessica_folder"]}')]

  cards = {
      'amexus': [],
      'amexca': [],
      'visaca': [],
      'chequs': [],
      'cheqca': [],
  }

  rename_count = 0  # accumulator so we don't overwrite with rename
  for full_file in files:
    file = full_file[0]
    # rename td debit files to separate debit & credit
    if 'accountactivity' in file:
      print(f'preprocessing: {file}')
      if input(f'--> is {file} a debit/chequing statement? (Y/n): ') == 'Y':
        oldfile = file
        full_file = ('/'.join(file.split('/')[:-1]) + f'/td{rename_count}.csv',
                     full_file[1])
        os.rename(oldfile, full_file[0])
        rename_count += 1

    # sort by statement
    if file.lower()[-4:] == '.csv':
      if 'Chase' in file:
        cards['chequs'].append(full_file)
      elif 'ofx' in file:
        cards['amexca'].append(full_file)
      elif 'accountactivity' in file:
        cards['visaca'].append(full_file)
      elif 'activity' in file:
        cards['amexus'].append(full_file)
      elif 'td' in file:
        cards['cheqca'].append(full_file)

  return cards


def preprocess(month, cards, save=False):
  '''Preprocesses CSVs from each bank into one DataFrame with consistent format

  Args:
    month: int, month number to process
    cards: dict, of list of tuples; key:bank, val:[(str filepath, str who)...]
    save: bool, whether to save csv to local, default=False

  Returns:
    list, preprocessed data
  '''
  with open('config.yaml', 'r', encoding='utf8') as infile:
    config = yaml.safe_load(infile)
  processed = []

  print('---> processing amex ca')
  for file in cards['amexca']:
    df = pd.read_csv(file[0], header=None)
    df = df[[0, 2, 3]]  # drop reference # and any comments
    df.columns = ['date', 'amount', 'item']
    df['debit'] = np.where(df['amount'] < 0, abs(df['amount']), np.nan)
    df['credit'] = np.where(df['amount'] >= 0, df['amount'], np.nan)
    df['who'] = file[1]
    df['card'] = 'amex ca'
    df['currency'] = 'CAD'
    df = df.reindex(columns=config['columns'], fill_value=np.nan)
    processed.append(df)

  print('---> processing amex us')
  for file in cards['amexus']:
    df = pd.read_csv(file[0], header=0)  # drop header column
    df.columns = ['date', 'item', 'amount']
    df['debit'] = np.where(df['amount'] < 0, abs(df['amount']), np.nan)
    df['credit'] = np.where(df['amount'] >= 0, df['amount'], np.nan)
    df['who'] = file[1]
    df['card'] = 'amex us'
    df['currency'] = 'USD'
    df = df.reindex(columns=config['columns'], fill_value=np.nan)
    processed.append(df)

  print('---> processing visa ca')
  for file in cards['visaca']:
    df = pd.read_csv(file[0], header=None)
    df = df.drop(labels=4, axis=1)  # drop balance tab
    df.columns = ['date', 'item', 'credit', 'debit']
    df['who'] = file[1]
    df['card'] = 'visa ca'
    df['currency'] = 'CAD'
    df = df.reindex(columns=config['columns'], fill_value=np.nan)
    processed.append(df)

  print('---> processing cheq ca')
  for file in cards['cheqca']:
    df = pd.read_csv(file[0], header=None)
    df = df.drop(labels=4, axis=1)  # drop balance tab
    df.columns = ['date', 'item', 'credit', 'debit']
    df['who'] = file[1]
    df['card'] = 'cheq ca'
    df['currency'] = 'CAD'
    df = df.reindex(columns=config['columns'], fill_value=np.nan)
    processed.append(df)

  print('---> processing cheq us')
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
    df = df.reindex(columns=config['columns'], fill_value=np.nan)
    processed.append(df)

  df = pd.concat(processed)
  # TODO: make this an exclusion list type thing
  df = df.loc[~df['item'].str.contains('THANK YOU')]
  # check date i.e. remove rows that aren't from the right month
  df['date'] = pd.to_datetime(df['date'])
  df = df[df['date'].dt.month == month]
  df['date'] = df['date'].dt.strftime(config['date_format'])
  df.sort_values(['date', 'who', 'card', 'item'], inplace=True)

  if save:
    df.to_csv(f'{config["output_folder"]}/spend.csv', header=None, index=None)
    print(f'----> transactions saved to {config["output_folder"]}/spend.csv')

  df = df.fillna('')
  return df.values.tolist()
