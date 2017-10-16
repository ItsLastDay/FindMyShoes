class Page:
    def __init__(self, url):
        """Page is created by text URL.

        `self.url` should point to this URL.
        """
        self.url = url

    def can_be_stored(self):
        """Checks that we are allowed to store this page.

        Checks for <META NAME="..."> tags. "noindex" keyword
        means that we should not store the page.

        Returns: boolean.
        """
        pass

    def fetch(self):
        """Query self.url, Download HTTP response of the server.

        Our crawler is polite, so it identifies itself as "findmyshoes_robot"
        Populates the result in this object (i.e. page content, children, etc.).

        If response status is not 200-OK, then subsequent calls to `can_be_stored` 
        and `can_be_crawled` should return empty values.

        Returns: nothing.
        """
        pass

    def children(self):
        """Returns all pages that current page points to.

        Should return empty list if <META NAME="..."> contains "nofollow".

        Returns: 
            list of `Page` objects.
        """
        pass

    def get_cleaned_response(self):
        """Returns text: HTML content of the page.

        Since we are mainly interested in HTML content
        of <body>...</body>, only that content is returned.

        Returns:
            str - content of <body> HTML tag.
        """
        pass
