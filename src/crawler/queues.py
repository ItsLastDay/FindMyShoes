
class DomainQueue:
    """Queue that contains domains that are not crawled by anyone

    Initially, this queue contains all of our domains. 
    Workers take domains from this queue when they are bored.
    """
    def __init__(self):
        pass

    def get_next_domain(self):
        """Fetch next domain for crawler to crawl.

        Returns: URL text, e.g. "http://www.asos.com/"
        """
        pass

    def is_empty(self):
        """Check that there are no domains to crawl.

        Returns: boolean.
        """
        pass


class CrawlQueue:
    """Worker-private queue that contains Page-s from one domain.
    """

    def __init__(self):
        pass


    def add_pages(self, pages_list):
        """Push pages to the queue.

        This function checks that Page-s with such URL-s
        were not yet added.

        Args:
            `pages_list`: list of Page-s that we want to add.

        Retuns: nothing.
        """
        pass

    def pop(self):
        """Pop the page on the top. Also return it.

        Returns: `Page` object.
        """
        pass

    def is_empty(self):
        """Check whether the queue is empty
        
        Returns:boolean
        """
        pass
