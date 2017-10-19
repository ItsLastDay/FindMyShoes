import requests

class URLGetter:
    USERAGENT = "findmyshoes_robot"

    session = requests.Session()
    session.headers.update({'User-Agent': USERAGENT})
    session.headers.update({'From': 'https://github.com/itslastday/findmyshoes'})

    @staticmethod
    def get_lines(url):
        response = URLGetter.get_response(url)
        lines = response.text.split('\n')
        return lines

    @staticmethod
    def get_response(url):
        return URLGetter.session.get(url)
