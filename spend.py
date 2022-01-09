import argparse
import os
import numpy as np
import pandas as pd
from datetime import datetime

PATH = '/Users/allengour/Downloads'
INPUT_DATE_FORMAT = '%m/%d/%Y'

def main(month):
    print('-> starting spend')
    files = os.listdir(PATH)
    amexus = []
    amexca = []
    visaca = []
    for file in files:
        if file[-4:] == '.csv':
            if 'ofx' in file:
                amexca.append(file)
            elif 'accountactivity' in file:
                visaca.append(file)
            elif 'activity' in file:
                amexus.append(file)
    frames = []

    print('--> processing amex us')
    for file in amexus:
        filepath = f'{PATH}/{file}'
        df = pd.read_csv(filepath, header=None)
        df = df.iloc[1: , :]
        df.columns = ['date', 'item', 'amount']
        df['category'] = np.nan
        df['card'] = 'amex us'
        df['CAD?'] = False
        frames.append(df)

    print('--> processing amex ca')
    for file in amexca:
        filepath = f'{PATH}/{file}'
        df = pd.read_csv(filepath, header=None)
        # df = df.drop(labels=5,axis=1)
        # df = df.drop(labels=4,axis=1)
        df = df.drop(labels=1,axis=1)
        df = df.reindex(columns=[0,3,2])
        df.columns = ['date', 'item', 'amount']
        df['category'] = np.nan
        df['card'] = 'amex ca'
        df['CAD?'] = True
        frames.append(df)

    print('--> processing visaca')
    for file in visaca:
        filepath = f'{PATH}/{file}'
        df = pd.read_csv(filepath, header=None)
        df = df.drop(labels=4,axis=1)
        df = df.fillna(0)
        df[4] = df[2] - df[3]
        df = df.drop(labels=3,axis=1)
        df = df.drop(labels=2,axis=1)
        df.columns = ['date', 'item', 'amount']
        df['category'] = np.nan
        df['card'] = 'visa ca'
        df['CAD?'] = True
        frames.append(df)

    df = pd.concat(frames)
    df = df.loc[~df['item'].str.contains('PAYMENT') | ~df['item'].str.contains('THANK YOU')]
    df = df.loc[~df['item'].str.contains('PREAUTHORIZED PAYMENT')]
    check_date = lambda d: d if datetime.strptime(d, INPUT_DATE_FORMAT).month == month else False
    df['date'] = df['date'].apply(check_date)
    df = df.loc[df['date'] != False]
    df.sort_values(['date', 'item'], inplace=True)
    print('-> done')

    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='preprocess spend')
    parser.add_argument('month', type=int, help='month to process for')
    args = parser.parse_args()
    df = main(args.month)
    df.to_csv(f'{PATH}/spend.csv', header=None, index=None)