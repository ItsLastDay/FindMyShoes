# Andrey
import re
from datetime import datetime
from logging import getLogger
from typing import Optional
from urllib import parse

from bs4 import BeautifulSoup, Tag

from url_getter import URLGetter

page_logger = getLogger("page")


class PageException(BaseException):
    pass


class Page:
    def __init__(self, domain_url: str, path: str = '/'):
        """Page is created by text URL.

        `self.url` should point to this URL.
        """
        # < scheme >: // < netloc > / < path >? < query >  # <fragment>
        if not path.startswith('/'):
            raise PageException("page path should start with '/'")

        scheme, netloc, domain_path = parse.urlsplit(domain_url)[:3]
        if netloc.endswith('/'):
            netloc = netloc[:-1]
        if domain_path.startswith('/'):
            domain_path = domain_path[1:]
        if len(domain_path) > 0:
            path = "/{}{}".format(domain_path, path)

        self._domain_url = "{}://{}".format(scheme, netloc)
        assert path.startswith('/') and (len(path) == 1 or path[1] != '/')
        self._path = path
        self._mtime = None
        self._text = None
        self._soup = None

    # Getters #
    def url(self):
        assert self._path.startswith('/')
        return self._domain_url + self._path

    def path(self):
        return self._path

    def domain_url(self):
        return self._domain_url

    def can_be_stored(self) -> Optional[bool]:
        """Checks that we are allowed to store this page.

        Checks for <META NAME="..."> tags. "noindex" keyword
        means that we should not store the page.

        Returns: boolean.
        """
        if self._soup is None:
            return None
        from storage import PageFilter
        if self._meta_tags_content_has_property("noindex"):
            page_logger.debug('Page "{}" cannot be stored because of noindex property'.format(self.url()))
            return False

        if not PageFilter.should_be_stored(self):
            page_logger.debug('Page "{}" cannot be stored because of PageFilter settings'.format(self.url()))
            return False
        page_logger.debug('OK, Page "{}" can be stored'.format(self.url()))
        return True

    def fetch(self):
        """Query self.url, Download HTTP response of the server.

        Our crawler is polite, so it identifies itself as "findmyshoes_robot"
        Populates the result in this object (i.e. page content, children, etc.).

        If response status is not 200-OK, then subsequent calls to `can_be_stored` 
        and `can_be_crawled` should return empty values.

        Returns: nothing.
        """
        page_logger.debug('Fetching page {}'.format(self.url()))
        response = URLGetter.get_response(self.url())
        if response.status_code != 200:
            page_logger.info("Failed to fetch page {} with status code {}".format(self.url(), response.status_code))
            assert not response.ok
        else:
            self._soup = BeautifulSoup(response.text, "lxml")

    def children(self) -> ['Page']:
        """Returns all pages that current page points to.

        Should return empty list if <META NAME="..."> contains "nofollow".

        Returns: 
            list of `Page` objects.
        """
        if self._soup is None or self._meta_tags_content_has_property("nofollow"):
            return []

        def get_path_from_link(link: Tag):
            path = link.get('href')
            if path is None:
                path = link.get('data-link')

                # If found an internal link and it doesn't lead to external site.
                if path is not None and path.startswith('/'):
                    path = "{}{}".format(self._domain_url, path)

            # href attribute is not present or leads to external domain.
            if path is None or (path.startswith('http') and not path.startswith(self._domain_url)):
                return None

            if path.startswith(self._domain_url):
                path = path[len(self._domain_url):]

            if not path.startswith('http') and not path.startswith('/'):
                path = '/' + path
            return path

        return list(map(lambda path: Page(self._domain_url, path),
                        filter(lambda path: path is not None and path.startswith('/'),
                               map(get_path_from_link, self._soup.find_all('a'))
                               )
                        )
                    )

    def get_cleaned_response(self) -> str:
        """Retrieve page's html content.
        :return: html content of page.
        """
        return str(self._soup)

    def mtime(self) -> datetime:
        """Returns the time the page was last fetched.
        This is useful for long-running web spiders that need to check for new robots.txt files periodically."""
        return self._mtime

    def modified(self) -> None:
        """Sets the time this page was last fetched to the current time."""
        self._mtime = datetime.now().time()

    def _meta_tags_content_has_property(self, property_name: str) -> bool:
        robots_metas = self._soup.findAll('meta', attrs={'name': re.compile(r'^robots', re.I)})

        def tag_content_has_property(tag):
            for key in ['CONTENT', 'content']:
                if tag.get(key, '').lower().find(property_name.lower()) != -1:
                    return True
            return False

        return any(map(tag_content_has_property, robots_metas))
