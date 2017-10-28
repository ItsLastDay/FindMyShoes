from page import Page
from abc import abstractmethod, ABC
import re
from collections import defaultdict


class PageFilter(ABC):
    # domain_url -> [PageFilter]
    domain_filters = defaultdict(lambda: [])

    @abstractmethod
    def should_be_stored(self, page: Page) -> bool:
        return True

    @staticmethod
    def should_be_stored(page: Page) -> bool:
        domain_url = page.domain_url()
        filters = PageFilter.domain_filters.get(domain_url, None)
        if filters is None:
            raise Exception("No filters for domain: {}".format(domain_url))
        result = True
        for f in filters:
            result = result and f.should_be_stored(page)
        return result


class RegexpPageFilter(PageFilter):
    def __init__(self, path_regexp: str = '*'):
        assert path_regexp.startswith('/')
        self._re = re.compile(path_regexp, flags=re.UNICODE | re.I)

    def should_be_stored(self, page: Page) -> bool:
        return self._re.match(page.path()) is not None


class PredicatePageFilter(PageFilter):
    def __init__(self, predicate):
        self._predicate = predicate

    def should_be_stored(self, page: Page) -> bool:
        return self._predicate(page)


# TODO formalize searching through breadcrumbs and use regular expressions.
def bonprix_page_is_shoes(page: Page) -> bool:
    if page._soup is None: return False
    spans = page._soup.select('div#breadcrumb a > span')
    return any(map(lambda span: span.text.lower().find('обувь') != -1, spans))


def respect_shoes_page_is_shoes(page: Page) -> bool:
    if page._soup is None: return False
    return any(map(lambda a: a.text.lower().find('обувь'), page._soup.select('ul.breadcrumbs a')))


def lamoda_page_is_shoes(page: Page) -> bool:
    if page._soup is None: return False
    spans = page._soup.select('div.breadcrumbs > span > a > span')
    return any(map(lambda span: span.text.lower().find('обувь') != -1, spans))


def ecco_shoes_is_shoes(page: Page) -> bool:
    if page._soup is None: return False
    spans = page._soup.select('div.i-breadcrumb > ul.i-breadcrumb-way > li > a > span')
    # TODO do something with children goods excluded this way.
    return any(map(lambda span: span.text.lower().find('обувь') != -1, spans))


def init_filters():
    # if not hasattr(PageFilter, 'domain_filters') or len(PageFilter.domain_filters) > 0:
    PageFilter.domain_filters = defaultdict(lambda: [])
    bonprix_filter = PageFilter.domain_filters["https://www.bonprix.ru"]
    bonprix_filter.append(RegexpPageFilter("/produkty/.*"))
    bonprix_filter.append(PredicatePageFilter(bonprix_page_is_shoes))

    respect_shoes_filter = PageFilter.domain_filters['https://www.respect-shoes.ru']
    respect_shoes_filter.append(PredicatePageFilter(respect_shoes_page_is_shoes))

    antoniobiaggi_filter = PageFilter.domain_filters['https://ru.antoniobiaggi.com']
    rs = "|".join(map(lambda s: r'/\d+-{}-.*'.format(s), ['sapogi',
                                                          'tufli',
                                                          'espadrili',
                                                          'baletki',
                                                          'krossovki',
                                                          'sabo',
                                                          'botinki',
                                                          'bosonozhki',
                                                          'mokasiny',
                                                          'kedy',
                                                          'botilony']))
    antoniobiaggi_filter.append(RegexpPageFilter(rs))

    lamoda_filter = PageFilter.domain_filters['https://www.lamoda.ru']
    lamoda_filter.append(RegexpPageFilter(r'/\w/\w{12}/shoes-.*'))
    lamoda_filter.append(PredicatePageFilter(lamoda_page_is_shoes))

    asos_filter = PageFilter.domain_filters['http://www.asos.com']
    asos_filter.append(RegexpPageFilter(r'/ru/.*')) # russian only
    #  нет хлебных крошек со словом 'Обувь' на русском сайте((
    # asos_filter.append(PredicatePageFilter(asos_page_is_shoes))

    # 'https://www.ecco-shoes.ru/catalog/634504/01053/'
    ecco_shoes_filter = PageFilter.domain_filters['https://www.ecco-shoes.ru']
    ecco_shoes_filter.append(RegexpPageFilter(r'/catalog/\d+/\d+/?'))
    ecco_shoes_filter.append(PredicatePageFilter(ecco_shoes_is_shoes))

init_filters()