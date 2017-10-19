from urllib import parse
import json
import os

from storage.basic_storage import BasicStorage, storage_logger


class LocalStorage(BasicStorage):
    def __init__(self, folder):
        super().__init__()
        self._folder = folder

    def put_page(self, page_url, page_content):
        storage_logger.debug("saving page with url: {}".format(page_url))
        netloc = parse.urlsplit(page_url)[1]
        folder = "{}/{}".format(self._folder, netloc)
        if not os.path.exists(folder):
            os.makedirs(folder)

        metadata = LocalStorage.page_metadata(page_url, page_content)
        filepath = "{}/{}".format(folder, metadata['path'])

        meta_filepath = filepath + ".meta"
        with open(meta_filepath, 'w') as f:
            storage_logger.debug("writing page metainfo to file {}".format(meta_filepath))
            f.write(json.dumps(metadata, sort_keys=True))

        # page_content = base64.b64encode(page_content.encode('utf-8')).decode('latin-1')
        with open(filepath, 'w') as f:
            storage_logger.debug("writing page content to file: {}".format(filepath))
            f.write(page_content)

    @staticmethod
    def create_storage() -> 'BasicStorage':
        # assuming we run at src/crawler folder of the repository.
        return LocalStorage("../../data/")
