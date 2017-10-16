class RobotsProvider:
    """Object that knows about "robots.txt" content of domains
    """

    @staticmethod
    def get_robots_delay(domain_url):
        """Get delay from "robots.txt" of `domain_url`

        Args:
            `domain_url`: URL, e.g. "ya.ru"

        Returns:
            floating point number - required delay in seconds. Defaults to 1 second.
        """
        pass

    @staticmethod
    def get_robots_banned_regexp(domain_url):
        """Get list of subdomains/pages that should not be crawled.

        Args:
            `domain_url`: URL, e.g. "ya.ru". The domain of interest.

        Returns:
            a compiled (see re.compile method) regexp. Let's call it `p`.
                When we want to
                check that URL `t` is banned by `domain_url`-s "robots.txt",
                `re.match(p, t)` should return `True`.
        """
        pass

    @staticmethod
    def can_be_crawled(domain_url, page_url):
        """
        Args:
            `domain_url`: URL, e.g. "ya.ru". The domain of interest.
            `page_url`: page URL.
        Returns:
            if page with given URL allowed to be crawled.
        """
        pass