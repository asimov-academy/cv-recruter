import gspread, googleapiclient, uuid
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build


SCOPE = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
CREDENTIALS = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', SCOPE)
CLIENT_SHEETS = gspread.authorize(CREDENTIALS)
CLIENT_DRIVE = build('drive', 'v3', credentials=CREDENTIALS)


class AccessResume:
    def __init__(self, sheets_name) -> None:
        self.sheet = CLIENT_SHEETS.open(sheets_name).sheet1

    def _get_all_values_in_sheet(self):
        return self.sheet.get_all_values()

    def get_resumes_id(self):
        return [line[-2].split('id=')[-1] for line in self._get_all_values_in_sheet()]
    
    def get_resumes_ids_unprocessed(self, know_id):
        ids = self.get_resumes_id()
        index = ids.index(know_id)
        return ids[index + 1:]

    def download_file(self, file_id):
        request = CLIENT_DRIVE.files().get_media(fileId=file_id)
        full_path = f'storage/{str(uuid.uuid4())}'
        with open(full_path, "wb") as file:
            downloader = googleapiclient.http.MediaIoBaseDownload(file, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        
        return full_path

    def check_file_access(file_id):
        try:
            CLIENT_DRIVE.files().get(fileId=file_id).execute()
        except googleapiclient.errors.HttpError as error:
            if error.resp.status == 404:
                raise Exception("File not found. Check the file ID or permissions.")
            else:
                raise Exception("Another error occurred.")
