import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage as CredStorage


# Code parts borrowed from
# https://developers.google.com/drive/v3/web/quickstart/python
class Storage:
    """The place where all crawled pages are stored"""

    def __init__(self):
        pass

    @staticmethod
    def create_storage():
        """Abstract out call of the __init__ from users.

        Since we may switch from keeping pages locally to
        keeping them in GDrive or wherever else, users
        should not be bothered by that.

        Returns: `Storage` object.
        """
        ret = Storage()

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

        ret.service = gdrive_service

        return ret

    def put_page(self, page_url, page_content):
        """Put page with conent into storage
        
        Args:
            `page_url` is a url, e.g. https://ya.ru
            `page_content` is that page's content, some text.

        This function checks that page with equal `page_content`
        was not stored before. 
        If this is the case, save the content into storage.

        Also, store meta-information somewhere in the storage,
        but separate from content: 
            URL 
            size of `page_content`

        Returns: nothing.
        """
        pass
