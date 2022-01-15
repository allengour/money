# spend

Allen & Jess' spending tracking, budgeting, and insights

### usage, right now
1. Download **csv** statements for a given month from bank/credit card websites. 
Sometimes one month's spending is across different statements (TD), or need to 
manually adjust the time range (Amex). TD debit and credit have same format and 
filename, so need to manually change credit card filenames to include "td".
2. Put Allen's files into a folder, and Jess' files into a folder. default 
`~/Desktop/allen` & `~/Desktop/jessica`.
3. Run `spend [month]` where `month` is the month number. `spend` is short for 
`python3 /.../spend.py [month]`
4. `spend.csv` is created in the output folder, default `~/Desktop`
5. Copy and paste as values the values in spend.csv into the correct `data` tab 
in the **spend** spreadsheet.
6. Do everything else manually and in Sheets.

### other
- only support TD, Amex, Chase, since that's all we use.
- savings/investment accounts tbd
- GCP? probs not that might be overkill
- FR: paste into Sheets with API
- don't like manually renaming TD credit card csv...
- train a model

### google sheets credentials
- not uploading credentials because that is illegal
- need a `credentials.json` file with API access credentials
- Desktop credentials in Google Sheets API under `allengour-personal` gcp
[project](https://console.cloud.google.com/apis/credentials?project=allengour-personal)
following [docs](https://developers.google.com/workspace/guides/create-credentials#desktop-app)
- google account has to be listed as a test user under oauth consent screen,
since the app is not 'published'