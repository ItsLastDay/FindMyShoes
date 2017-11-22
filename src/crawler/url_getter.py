import requests

def _get_session():
    USERAGENT = "findmyshoes_robot"

    session = requests.Session()
    session.headers.update({'User-Agent': USERAGENT})
    session.headers.update({'From': 'https://github.com/itslastday/findmyshoes'})

    return session


class URLGetter:
    USERAGENT = "findmyshoes_robot"

    session = _get_session()

    @classmethod
    def restart_sesison(cls):
        cls.session = _get_session()

    @staticmethod
    def get_lines(url):
        response = URLGetter.get_response(url)
        lines = response.text.split('\n')
        return lines

    @staticmethod
    def get_response(url):
        return URLGetter.session.get(url)
