from typing import Optional
from urllib import parse
from datetime import datetime
from collections import namedtuple
from math import inf

from robots.config import robots_logger, URLGetter


class RobotsParserException(BaseException):
    pass


class MemberGroupData:
    Entry = namedtuple("Entry", ['allow', 'template'])

    def __init__(self, name):
        self.name = name
        self.lines = []
        self.other_data = {}

    def add_line(self, allow: bool, path: str) -> None:
        path = path.strip()

        # if "disallow:" -> yandex interprets as "allow: *", google skips
        if not allow and len(path) == 0:
            self.add_line(True, "*")
            return

        # "allow: " skipped by both.
        if allow and len(path) == 0:
            return
        template = MemberGroupData._get_template_split(path)
        new_entry = MemberGroupData.Entry(allow, template)
        self.lines.append(new_entry)

    def allowed(self, url: str):
        # TODO optimize to avoid sorting lines on each query.
        def entry_sorter(entry):
            return -len('*'.join(entry.template))
        self.lines = sorted(self.lines, key=entry_sorter)

        # Following does not work correctly with question-marks: https://www.google.com/?hl= -> /
        # path, query, fragment = parse.urlsplit(url)[2:]
        # path = path + query + fragment

        domain = parse.urlsplit(url)[1]
        assert len(domain) > 0
        if url.find(domain) == -1:
            raise RobotsParserException("url {} domain extraction error".format(url))
        path = url[url.find(domain) + len(domain):]

        for l in self.lines:
            if MemberGroupData._line_matches_template(path, l.template):
                return l.allow
        return True

    def add_other(self, name: str, value):
        if name in self.other_data:
            log_message = "already has parameter {} with value {}, " \
                          "setting new value {}".format(name, self.other_data[name], value)
            robots_logger.info(log_message)
        self.other_data[name] = value

    def get_other(self, name: str):
        return self.other_data.get(name, None)

    @staticmethod
    def _line_matches_template(line: str, template: [str]):
        previous_is_star = False
        for i, t in enumerate(template):
            if (not previous_is_star and not line.startswith(t)) or line.find(t) == -1:
                return False
            t_pos = line.find(t)
            assert t_pos != -1
            line = line[t_pos + len(t):]
            previous_is_star = len(t) == 0
        return True

    @staticmethod
    def _get_template_split(path: str) -> [str]:
        if len(path) == 0:
            return True
        if len(path) > 2 and path[:-1] == "$" and path[:-2] == "$":
            path = path[:-1]
        ampersand_pos = path.find('$')
        if ampersand_pos not in (-1, len(path) - 1):
            raise RobotsParserException("Error while parsing template for line \"{}\"".format(path))

        if path[-1] != '$':
            path += '*'
        template_split = []
        while path.find('*') != -1:
            star_pos = path.find('*')
            if star_pos > 0:
                template_split.append(path[:star_pos])
            template_split.append('')
            path = path[star_pos + 1:]

        if len(path) > 0:
            template_split.append(path)

        return template_split


class RobotsParser:
    def __init__(self, robots_url, deferred_read=False):
        self.set_url(robots_url)
        self._data = {}
        if not deferred_read:
            self.read()
        self._url = None
        self._mtime = None

    def set_url(self, robots_url):
        """Sets the URL referring to a robots.txt file."""
        self._url = robots_url

    def read(self):
        """Reads the robots.txt URL and feeds it to the parser."""
        lines = URLGetter.get_lines(self._url)
        self.parse(lines)
        self.modified()

    def parse(self, lines: [str]):
        member_group_data = None
        for l in lines:
            if l.find('#') != -1:
                l = l[:l.find('#')]
            l = l.strip()
            if len(l) == 0:
                continue
            v = l.split(':')
            param, value = v[0], ':'.join(v[1:])
            param = param.lower()
            value = value.strip()
            if param == 'user-agent':
                if value not in self._data:
                    self._data[value] = MemberGroupData(value)
                member_group_data = self._data[value]
            elif param == 'disallow' or param == 'allow':
                member_group_data.add_line(param == 'allow', value)
            elif param == 'sitemap':
                member_group_data.add_other('sitemap', value)
            elif param == 'crawl-delay':
                member_group_data.add_other('crawl-delay', float(value))
            else:
                robots_logger.info("param {} is ignored in line {}".format(param, l))

    def can_fetch(self, useragent, url: str) -> bool:
        """Returns True if the useragent is allowed to fetch the url
        according to the rules contained in the parsed robots.txt file."""
        member_group_data = self._member_group_data(useragent)
        assert member_group_data is not None
        return member_group_data.allowed(url)

    def mtime(self):
        """Returns the time the robots.txt file was last fetched.
        This is useful for long-running web spiders that need to check for new robots.txt files periodically."""
        return self._mtime

    def modified(self):
        """Sets the time the robots.txt file was last fetched to the current time."""
        self._mtime = datetime.now().time()

    def crawl_delay(self, useragent: str) -> Optional[float]:
        """Returns the value of the Crawl-delay parameter from robots.txt for the useragent in question.
        If there is no such parameter or it doesn’t apply to the useragent specified or
        the robots.txt entry for this parameter has invalid syntax, return None."""
        member_group_data = self._member_group_data(useragent)
        assert member_group_data is not None
        return member_group_data.get_other('crawl-delay')

    def request_rate(self, useragent: str) -> Optional[float]:
        """Returns the contents of the Request-rate parameter from robots.txt
        in the form of a namedtuple() (requests, seconds).
        If there is no such parameter or it doesn’t apply to the useragent specified
        or the robots.txt entry for this parameter has invalid syntax, return None."""
        # TODO implement
        return None

    def _member_group_data(self, useragent: str) -> Optional[MemberGroupData]:
        """returns one most appropriate member-group entry"""

        # need to start searching from the longest names.
        # all the way to '*'
        def sorter_key(member_group_name: str):
            if member_group_name == "*":
                return inf
            return -len(member_group_name)

        names_sorted = sorted(self._data.keys(), key=sorter_key)
        for name in names_sorted:
            if useragent.startswith(name) or name == "*":
                return self._data[name]
        return None
