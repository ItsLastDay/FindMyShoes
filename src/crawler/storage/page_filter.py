from page import Page
from abc import abstractmethod, ABC
import re
from collections import defaultdict


class PageFilter(ABC):
    domain_filters = defaultdict()

    @staticmethod
    def init():
        # domain_url -> [PageFilter]
        PageFilter.domain_filters = defaultdict(lambda: [])
        bonprix_filter = PageFilter._get_domain_filters("https://www.bonprix.ru")
        bonprix_filter.append(RegexpPageFilter("/produkty/.*"))
        bonprix_filter.append(BreadcrumbPageFilter('div#breadcrumb a > span', 'обувь'))

        respect_shoes_filter = PageFilter._get_domain_filters('https://www.respect-shoes.ru')
        respect_shoes_filter.append(BreadcrumbPageFilter('ul.breadcrumbs a', 'обувь'))

        antoniobiaggi_filter = PageFilter._get_domain_filters('https://ru.antoniobiaggi.com')
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

        lamoda_filter = PageFilter._get_domain_filters('https://www.lamoda.ru')
        lamoda_filter.append(RegexpPageFilter(r'/\w/\w{12}/shoes-.*'))
        lamoda_filter.append(BreadcrumbPageFilter('div.breadcrumbs > span > a > span', 'обувь'))

        asos_filter = PageFilter._get_domain_filters('http://www.asos.com')
        asos_filter.append(RegexpPageFilter(r'/ru/.+prd/[0-9]{7}'))  # russian only
        asos_templates = ['Туфли, ботинки и кеды', 'Новинки: обувь', 'обувь']
        asos_filter.append(BreadcrumbPageFilter('div#breadcrumb > ul > li > a', asos_templates))

        # 'https://www.ecco-shoes.ru/catalog/634504/01053/'
        ecco_shoes_filter = PageFilter._get_domain_filters('https://www.ecco-shoes.ru')
        ecco_shoes_filter.append(RegexpPageFilter(r'/catalog/\d+/\d+/?'))
        ecco_shoes_filter.append(
            BreadcrumbPageFilter('div.i-breadcrumb > ul.i-breadcrumb-way > li > a > span', 'обувь'))

    @abstractmethod
    def should_be_stored(self, page: Page) -> bool:
        return True

    @staticmethod
    def should_be_stored(page: Page) -> bool:
        domain_url = page.domain_url()
        filters = PageFilter._get_domain_filters(domain_url)
        if filters is None:
            raise Exception("No filters for domain: {}".format(domain_url))
        result = True
        for f in filters:
            result = result and f.should_be_stored(page)
        return result

    @staticmethod
    def _simplified_domain_url(domain_url: str) -> str:
        simple_domain = str(domain_url)
        while simple_domain.endswith('/'):
            simple_domain = simple_domain[:-1]
        if simple_domain.startswith('https://'):
            simple_domain = simple_domain[len('https://'):]
        if simple_domain.startswith('http://'):
            simple_domain = simple_domain[len('http://'):]
        if simple_domain.startswith('www.'):
            simple_domain = simple_domain[len('www.'):]
        return simple_domain

    @staticmethod
    def _get_domain_filters(domain_url: str) -> ['PageFilter']:
        simple_domain = PageFilter._simplified_domain_url(domain_url)
        return PageFilter.domain_filters[simple_domain]


class RegexpPageFilter(PageFilter):
    def __init__(self, path_regexp: str = '*'):
        assert path_regexp.startswith('/')
        self._re = re.compile(path_regexp, flags=re.UNICODE | re.I)

    def should_be_stored(self, page: Page) -> bool:
        return self._re.match(page.path()) is not None


class BreadcrumbPageFilter(PageFilter):
    def __init__(self, css_spans_selector, templates):
        self.spans_selector = css_spans_selector

        def filter_from_template(template):
            return lambda span: span.text.lower().find(template) != -1

        if type(templates) == list:
            self.span_filters = list(map(filter_from_template, templates))
        else:
            assert type(templates) == str
            self.span_filters = [filter_from_template(templates)]

    def should_be_stored(self, page: Page) -> bool:
        if page._soup is None: return False
        spans = page._soup.select(self.spans_selector)
        result = False
        for f in self.span_filters:
            result = result or any(map(f, spans))
        return result


class PredicatePageFilter(PageFilter):
    def __init__(self, predicate):
        self._predicate = predicate

    def should_be_stored(self, page: Page) -> bool:
        return self._predicate(page)
