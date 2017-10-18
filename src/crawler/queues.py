import queue
from page import Page


class DomainQueue:
    """Queue that contains domains that are not crawled by anyone

    Initially, this queue contains all of our domains. 
    Workers take domains from this queue when they are bored.
    """

    def __init__(self):
        pass

    def get_next_domain(self) -> str:
        """Fetch next domain for crawler to crawl.

        Returns: URL text, e.g. "http://www.asos.com/"
        """
        pass

    def is_empty(self) -> bool:
        """Check that there are no domains to crawl.

        Returns: boolean.
        """
        pass


# Andrey
class CrawlQueue:
    """Worker-private queue that contains Page-s from one domain.
    """

    def __init__(self):
        self._used_pages_urls = set()
        self._pages_queue = queue.Queue()

    def add_pages(self, pages_list: [Page]) -> None:
        """Push pages to the queue.

        This function checks that Page-s with such URL-s
        were not yet added.

        Args:
            `pages_list`: list of Page-s that we want to add.

        Retuns: nothing.
        """
        for p in pages_list:
            if p.url not in self._used_pages_urls:
                self._used_pages_urls.add(p.url)
                self._pages_queue.put(p)
        pass

    def pop(self) -> Page:
        """Pop the page on the top. Also return it.

        Returns: `Page` object.
        """
        return self._pages_queue.get_nowait()

    def is_empty(self) -> bool:
        """Check whether the queue is empty
        
        Returns:boolean
        """
        return self._pages_queue.empty()
