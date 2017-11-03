from urllib import parse
import json
import os

from storage.basic_storage import BasicStorage, storage_logger


class LocalStorage(BasicStorage):
    def __init__(self, folder):
        super().__init__()
        self._folder = folder

    def put_page(self, page_url, page_content):
        storage_logger.debug("Saving page with url: {}".format(page_url))
        netloc = parse.urlsplit(page_url)[1]
        folder = "{}/{}".format(self._folder, netloc)
        if not os.path.exists(folder):
            os.makedirs(folder)

        metadata = LocalStorage.page_metadata(page_url, page_content)

        # Checking if a duplicate page was crawled earlier.
        page_hash = metadata['hash']
        if not self.put_page_if_not_exist(page_hash, (page_content, metadata)):
            _, duplicate_metadata = self.pages[page_hash]
            duplicate_url = duplicate_metadata['url']
            msg = "Saving page {} failed, duplication with page {}".format(metadata['url'], duplicate_url)
            storage_logger.debug(msg)
            return
        filepath = "{}/{}".format(folder, metadata['path'])

        meta_filepath = filepath + ".meta"
        with open(meta_filepath, 'w') as f:
            storage_logger.debug("Writing page metainfo to file {}".format(meta_filepath))
            f.write(json.dumps(metadata, sort_keys=True))

        # page_content = base64.b64encode(page_content.encode('utf-8')).decode('latin-1')
        with open(filepath + '.html', 'w') as f:
            storage_logger.debug("Writing page content to file: {}".format(filepath))
            f.write(page_content)

    @staticmethod
    def create_storage() -> 'BasicStorage':
        # assuming we run at src/crawler folder of the repository.
        return LocalStorage("../../data/")
