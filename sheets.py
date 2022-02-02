'''sends preprocessed data to Sheets'''

import os.path
import yaml
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def insert(transactions):
  '''Inserts data into the spreadsheet

  Args:
    transactions: list, of transactions, adhering to the data schema

  Returns:
    int, number of rows inserted
  '''
  with open('config.yaml', 'r', encoding='utf8') as infile:
    config = yaml.safe_load(infile)

  # Appropriated from https://developers.google.com/sheets/api/quickstart/python
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # auto created when the authorization flow completes for the first time.
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', config['scope'])
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file('credentials.json',
                                                       config['scope'])
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w', encoding='utf8') as token:
      token.write(creds.to_json())

  try:
    service = build('sheets', 'v4', credentials=creds)

    # call Sheets API
    sheet = service.spreadsheets()

    request = sheet.values().append(spreadsheetId=config['spreadsheet_id'],
                                    range=config['range'],
                                    valueInputOption='USER_ENTERED',
                                    insertDataOption='INSERT_ROWS',
                                    body={
                                        'range': config['range'],
                                        'majorDimension': 'ROWS',
                                        'values': transactions,
                                    })

    response = request.execute()
    print(f'--> inserted {response["updates"]["updatedRows"]} rows' +
          f' into cell range {response["updates"]["updatedRange"]}')
    print('--> spend: https://docs.google.com/spreadsheets/d/' +
          f'{response["spreadsheetId"]}/edit#gid=756239425')
    return response['updates']['updatedRows']

  except HttpError as err:
    print(err)
