import urllib
from urllib import parse
from urllib import robotparser
from config import useragent


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
        robots_parser = RobotsProvider._get_robots_parser(domain_url)
        pass

    @staticmethod
    def can_be_crawled(domain_url: str, page_url: str) -> bool:
        """
        Args:
            `domain_url`: URL, e.g. "ya.ru". The domain of interest.
            `page_url`: page URL.
        Returns:
            if page with given URL allowed to be crawled.
        """

        if not RobotsProvider._is_page_in_domain(page_url, domain_url):
            raise "page \"{}\" does not belong to domain \"{}\"".format(domain_url, page_url)
        robots_parser = RobotsProvider._get_robots_parser(domain_url)
        return robots_parser.can_fetch(useragent, page_url)

    @staticmethod
    def _is_page_in_domain(page_url: str, domain_url: str) -> bool:
        def _simplified_url(url: str) -> str:
            # netloc + path
            netloc, path = parse.urlsplit(url)[1:3]
            if netloc[:3] == "www":
                netloc = netloc[3:]
            return netloc + path

        domain_url = _simplified_url(domain_url)
        page_url = _simplified_url(page_url)
        return page_url.find(domain_url) != -1

    @staticmethod
    def _get_robots_parser(domain_url: str) -> robotparser.RobotFileParser:
        _robots = RobotsProvider._robots
        if not domain_url in _robots:
            robots_txt_url = domain_url + "/robots.txt"
            _robots[domain_url] = robotparser.RobotFileParser(robots_txt_url)
        _robots[domain_url].read()
        return _robots.get(domain_url, None)
