# Andrey
from datetime import datetime
from logging import getLogger
from typing import Optional
import re

from bs4 import BeautifulSoup

from robots.config import URLGetter

page_logger = getLogger("page")


class Page:
    def __init__(self, url):
        """Page is created by text URL.

        `self.url` should point to this URL.
        """
        self._url = url
        self._mtime = None
        self._text = None
        self._soup = None

    def can_be_stored(self) -> Optional[bool]:
        """Checks that we are allowed to store this page.

        Checks for <META NAME="..."> tags. "noindex" keyword
        means that we should not store the page.

        Returns: boolean.
        """
        if self._soup is None:
            return None
        return not self._meta_tags_content_has_property("noindex")

    def fetch(self):
        """Query self.url, Download HTTP response of the server.

        Our crawler is polite, so it identifies itself as "findmyshoes_robot"
        Populates the result in this object (i.e. page content, children, etc.).

        If response status is not 200-OK, then subsequent calls to `can_be_stored` 
        and `can_be_crawled` should return empty values.

        Returns: nothing.
        """
        page_logger.debug('Fetching page {}'.format(self._url))
        response = URLGetter.get_response(self._url)
        if response.status_code != 200:
            page_logger.info("Failed to fetch page {} with status code {}".format(self._url, response.status_code))
            assert not response.ok
        else:
            self._soup = BeautifulSoup(response.text)

    def children(self) -> ['Page']:
        """Returns all pages that current page points to.

        Should return empty list if <META NAME="..."> contains "nofollow".

        Returns: 
            list of `Page` objects.
        """
        if self._soup is None or self._meta_tags_content_has_property("nofollow"):
            return []

        return list(map(lambda link: Page(link.get('href')), self._soup.find_all('a')))

    def get_cleaned_response(self) -> str:
        """Returns text: HTML content of the page.

        Since we are mainly interested in HTML content
        of <body>...</body>, only that content is returned.

        Returns:
            str - content of <body> HTML tag.
        """
        return self._soup.body.text

    def mtime(self) -> datetime:
        """Returns the time the page was last fetched.
        This is useful for long-running web spiders that need to check for new robots.txt files periodically."""
        return self._mtime

    def modified(self) -> None:
        """Sets the time this page was last fetched to the current time."""
        self._mtime = datetime.now().time()

    def _meta_tags_content_has_property(self, property: str) -> bool:
        robots_metas = self._soup.findAll('meta', attrs={'name': re.compile(r'^robots', re.I)})

        def tag_content_has_property(tag):
            for key in ['CONTENT', 'content']:
                if tag.get(key, '').lower().find(property.lower()) != -1:
                    return True
            return False

        return any(map(tag_content_has_property, robots_metas))
