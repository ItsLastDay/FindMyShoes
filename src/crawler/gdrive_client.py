import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage as CredStorage


def get_gdrive_service():
    SCOPES = 'https://www.googleapis.com/auth/drive'
    APPLICATION_NAME = 'FindMyShoes'

    credential_path = "./api_creds.json"
    store = CredStorage(credential_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets('./client_secret.json', SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, None)
        print('Storing credentials to ' + credential_path)

    http = credentials.authorize(httplib2.Http())
    gdrive_service = discovery.build('drive', 'v3', http=http)

    return gdrive_service
