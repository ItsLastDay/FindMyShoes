import io

import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage as CredStorage

from apiclient.http import MediaIoBaseUpload


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


def is_file_exists(service, fname):
    # https://developers.google.com/drive/v3/web/search-parameters
    already_has_file = service.files().list(
            q='name = "{}"'.format(fname),
            pageSize=1,
            fields='files(id, name)'
        ).execute()
    return bool(already_has_file.get('files', []))


def save_file(service, fname, content, mimetype='text/html', parents=None):
    # https://developers.google.com/api-client-library/python/guide/media_upload
    media = MediaIoBaseUpload(
            io.StringIO(content),
            mimetype=mimetype
        )

    meta = dict(name=fname)
    # https://developers.google.com/drive/v3/web/folder
    if parents:
        meta['parents'] = parents

    # https://developers.google.com/drive/v3/web/manage-uploads
    print(service.files().create(
            body=meta,
            media_body=media
        ).execute())
