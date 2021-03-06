from abc import ABC, abstractmethod
import hashlib
from urllib import parse
from logging import getLogger

storage_logger = getLogger("storage")


class BasicStorage(ABC):
    def __init__(self):
        self.pages = dict()

    @staticmethod
    @abstractmethod
    def create_storage() -> 'BasicStorage':
        return BasicStorage()

    @abstractmethod
    def put_page(self, page_url: str, page_content: str):
        pass

    def put_page_if_not_exist(self, hash, page_info) -> bool:
        """
        Puts has into dictionary if not exist
        :param hash:
        :param page_info: Page info to save for debug.
        :return True if insert into dictionary is successful.
        """
        if hash in self.pages:
            return False
        self.pages[hash] = page_info
        return True

    @staticmethod
    def page_metadata(page_url: str, page_content) -> dict:
        content_hash = hashlib.md5(page_content.encode('utf-8')).hexdigest()
        filepath = BasicStorage._get_path_for_page(page_url)
        metadata = dict(
            path=filepath,
            url=page_url,
            size=len(page_content),
            hash=content_hash
        )
        return metadata

    @staticmethod
    def _get_path_for_page(page_url: str) -> str:
        page_path, query, fragment = parse.urlsplit(page_url)[2:]
        page_path = '/' + page_path
        if len(query) != 0:
            page_path += '?' + query
        if len(fragment) != 0:
            page_path += '#' + fragment
        while page_path.startswith('/'):
            page_path = page_path[1:]
        return "_" + page_path.replace('/', '##')
