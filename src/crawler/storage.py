import hashlib
import json
import io

from apiclient.http import MediaIoBaseUpload

from gdrive_client import get_gdrive_service


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
        ret.service = get_gdrive_service()

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
            path to file

        Returns: nothing.
        """
        content_hash = hashlib.md5(page_content.encode('utf-8')).hexdigest()

        metadata = dict(
            path=content_hash,
            url=page_url,
            size=len(page_content)
        )
        

        # Save metadata only if content was not seen before.
        if self._save_file_if_not_exist(content_hash, page_content):
            self._save_file_if_not_exist('{}.meta'.format(page_url), json.dumps(metadata, sort_keys=True))
            

    def _save_file_if_not_exist(self, filename, content, mimetype='text/html'):
        """
        Returns: boolean flag "did we save this file?".
        """
        # https://developers.google.com/drive/v3/web/search-parameters
        already_has_file = self.service.files().list(
                q='name = "{}"'.format(filename),
                pageSize=1,
                fields='files(id, name)'
            ).execute()
        if already_has_file.get('files', []):
            # TODO: switch to logging
            print(already_has_file)
            return False

        # https://developers.google.com/api-client-library/python/guide/media_upload
        media = MediaIoBaseUpload(
                io.StringIO(content),
                mimetype=mimetype
            )

        # https://developers.google.com/drive/v3/web/manage-uploads
        self.service.files().create(
                body=dict(name=filename),
                media_body=media
            ).execute()

        return True
