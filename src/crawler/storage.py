


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
        pass

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
