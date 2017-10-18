import time
from collections import deque
from logging import getLogger

from page import Page
import gdrive_client


queues_logger = getLogger("queues")


class DomainQueue:
    """Queue that contains domains that are not crawled by anyone

    Initially, this queue contains all of our domains. 
    Workers take domains from this queue when they are bored.
    """

    def __init__(self):
        self._next_domain = None

    def get_next_domain(self) -> str:
        """Fetch next domain for crawler to crawl.

        Returns: URL text, e.g. "http://www.asos.com/"
        """
        return self._next_domain

    def has_next(self) -> bool:
        """Check that there are domains to crawl.

        Also store the next domain in `self._next_domain`.
        And remove it from the queue.

        Returns: boolean.
        """

        QUEUE_FILE_NAME = './domain_queue.txt'

        
        lines = None
        with open(QUEUE_FILE_NAME, 'r') as f:
            lines = f.read().strip().splitlines()
            if not lines:
                return False

        self._next_domain = lines[0]
        with open(QUEUE_FILE_NAME, 'w') as f:
            f.write('\n'.join(lines[1:]))

        return True


# Andrey & Mike
class CrawlQueue:
    """Worker-private queue that contains Page-s from one domain.
    """

    def __init__(self):
        self._used_pages_urls = set()
        self._pages_queue = deque()

    def add_pages(self, pages_list: [Page]) -> None:
        """Push pages to the queue.

        This function checks that Page-s with such URL-s
        were not yet added.

        Args:
            `pages_list`: list of Page-s that we want to add.

        Retuns: nothing.
        """
        queues_logger.debug("Adding pages {}".format(list(map(lambda x: x._url, pages_list))))
        for p in pages_list:
            if p._url not in self._used_pages_urls:
                self._used_pages_urls.add(p._url)
                self._pages_queue.append(p)

    def pop(self) -> Page:
        """Pop the page on the top. Also return it.

        Returns: `Page` object.
        """
        return self._pages_queue.popleft()

    def is_empty(self) -> bool:
        """Check whether the queue is empty
        
        Returns:boolean
        """
        return not bool(self._pages_queue)
