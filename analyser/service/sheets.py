import gspread
from oauth2client.service_account import ServiceAccountCredentials


scope = ['https://www.googleapis.com/auth/spreadsheets']
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(credentials)

sheet = client.open('[1º etapa - Vaga] Líder Comercial (Responses)').sheet1
data = sheet.get_all_values()