import base64
import json

from storage import gdrive_client
from storage.basic_storage import BasicStorage, storage_logger


# Code parts borrowed from
# https://developers.google.com/drive/v3/web/quickstart/python
class GDriveStorage(BasicStorage):
    """The place where all crawled pages are stored"""

    def __init__(self):
        super().__init__()
        self._service = gdrive_client.get_gdrive_service()
        self._meta_folder_id = self._service.files().list(q='name="metainfo"',
                                                          fields='files(id)').execute()['files'][0]['id']
        self._pages_folder_id = self._service.files().list(q='name="pages"', fields='files(id)').execute()['files'][0][
            'id']

    @staticmethod
    def create_storage():
        """Abstract out call of the __init__ from users.

        Since we may switch from keeping pages locally to
        keeping them in GDrive or wherever else, users
        should not be bothered by that.

        Returns: `Storage` object.
        """
        return GDriveStorage()

    def put_page(self, page_url: str, page_content: str) -> None:
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
            path to file

        Returns: nothing.
        """
        metadata = GDriveStorage.page_metadata(page_url, page_content)
        metadata['path'] = metadata['hash']
        page_content = base64.b64encode(page_content.encode('utf-8')).decode('latin-1')

        # Save metadata only if content was not seen before.
        if self._save_file_if_not_exist('{}'.format(metadata['path']), page_content, parents=[self._pages_folder_id]):
            self._save_file_if_not_exist('{}.meta'.format(metadata['path']), json.dumps(metadata, sort_keys=True),
                                         parents=[self._meta_folder_id])

    def _save_file_if_not_exist(self, filename, content, mimetype='text/html', parents=None):
        """
        Returns: boolean flag "did we save this file?".
        """
        if gdrive_client.is_file_exists(self._service, filename):
            storage_logger.info("File {} already exists".format(filename))
            return False

        gdrive_client.save_file(self._service, filename, content, mimetype, parents=parents)
        return True
