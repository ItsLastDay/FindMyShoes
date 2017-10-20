# from urllib import parse

from url_getter import URLGetter
from page import Page
from robots.parser import RobotsParser
from robots.config import robots_logger


class RobotsProviderException(BaseException):
    pass


class RobotsProvider:
    _robots = {}

    @staticmethod
    def get_robots_delay(domain_url: str):
        """Get delay from "robots.txt" of `domain_url`

        Args:
            `domain_url`: URL, e.g. "ya.ru"

        Returns:
            floating point number - required delay in seconds. Defaults to 1 second.
        """

        real_domain_url = Page(domain_url).domain_url()
        robots_parser = RobotsProvider._get_robots_parser(real_domain_url)
        delay = robots_parser.crawl_delay(URLGetter.USERAGENT)
        if delay is None:
            return 1
        else:
            return delay

    @staticmethod
    def can_be_crawled(page: Page) -> bool:
        """
        Args:
            `domain_url`: URL, e.g. "ya.ru". The domain of interest.
            `page_url`: page URL.
        Returns:
            if page with given URL allowed to be crawled.
        """

        robots_logger.debug("checking page is crawlable {} for domain {}".format(page.url(), page.domain_url()))
        robots_parser = RobotsProvider._get_robots_parser(page.domain_url())
        return robots_parser.can_fetch(URLGetter.USERAGENT, page.path())

    @staticmethod
    def _get_robots_parser(domain_url: str) -> RobotsParser:
        while domain_url.endswith('/'):
            domain_url = domain_url[:-1]
        _robots = RobotsProvider._robots
        if domain_url not in _robots:
            robots_txt_url = domain_url + "/robots.txt"
            robots_logger.debug("creating RobotsParser for URL(robots.txt): {}".format(robots_txt_url))
            _robots[domain_url] = RobotsParser(robots_txt_url)
        return _robots.get(domain_url, None)
