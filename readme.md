# spend

Allen & Jess' spending tracking, budgeting, and insights

### usage, right now
1. Download **csv** statements for a given month from bank/credit card websites. 
Sometimes one month's spending is across two statements (TD), or need to 
manually adjust the time range (Amex). TD debit and credit have same format and 
filename, so need to tell the script which files are debit
2. Put Allen's files into a folder, and Jess' files into a folder. default 
`~/Desktop/allen` & `~/Desktop/jessica`
3. Run `spend [month]` where `month` is the month number. `spend` is short for 
`python3 /.../spend.py [month]`
4. Rows are preprocessed into same schema then uploaded to the spend sheet. Can
tell script to create `spend.csv` by specifying `save=True` in `preprocess()`
5. Do categories manually in Sheets.

### notes
- only support TD, Amex, Chase, since that's all we use.

### google sheets credentials
- not uploading credentials because that is illegal
- need a `credentials.json` file with API access credentials
- Desktop credentials in Google Sheets API under `allengour-personal` gcp
[project](https://console.cloud.google.com/apis/credentials?project=allengour-personal)
following [docs](https://developers.google.com/workspace/guides/create-credentials#desktop-app)
- google account has to be listed as a test user under oauth consent screen,
since the app is not 'published'
