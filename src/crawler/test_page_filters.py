import time

from page import Page
from storage.page_filter import PageFilter

def general_test(domain_url, tests):
    filter = PageFilter._get_domain_filters(domain_url)
    for path, expected in tests:
        if type(expected) != tuple:
            expected = (expected, )
        p = Page(domain_url, path)
        p.fetch()
        time.sleep(0.5)
        result = tuple(map(lambda f: f.should_be_stored(p), filter))
        result_str = "[ OK ]" if result == expected else "[FAIL]"
        print('{} URL: "{}", got {}, expected: {}'.format(result_str, domain_url + path, result, expected))


def bonprix_test():
    domain_url = 'https://www.bonprix.ru/'
    tests = [('/produkty', (False, False)),
             ('/produkty/', (True, False)),
             ('/produkty/polusapozhki-svetlo-seryj-907494/', (True, True)),
             ('/robots.txt', (False, False)),
             ('/kategoriya/dlia-zhienshchin-novinki-feshn-triendy/', (False, False))
             ]
    general_test(domain_url, tests)


def respect_shoes_test():
    domain_url = 'https://www.respect-shoes.ru'
    tests = [
        ('/robots.txt', False),
        ('/botinki_iz_nubuka_svetlo_korichnevogo_tsveta_na_mekhu_vk22_101576', True)
    ]
    general_test(domain_url, tests)


def antoniobiaggi_test():
    domain_url = 'https://ru.antoniobiaggi.com/'
    tests = [
        ('/47541-botinki-zhenskie-zamshevye.html', True),
        ('/47353-sapogi-zhenskie-zamshevye.html', True),
        ('/47360-tufli-zhenskie-lakovye.html', True),
        ('/46489-tufli-zhenskie.html', True),
        ('/47568-krossovki-zhenskie-kozhanye.html', True),
        ('/46324-bosonozhki-zhenskie-zamshevye.html', True),
        ('/47541-botinki-zhenskie-zamshevye.html', True),
        ('/46287-bosonozhki-zhenskie-zamshevye.html', True),
        ('/3-women', False),
        ('/', False)
    ]
    general_test(domain_url, tests)


def lamoda_test():
    domain_url = 'https://www.lamoda.ru/'
    tests = [
        ('/c/277/shoes-sandalii-dlya-malchikov/', (False, True)),
        ('/p/ch001abrgi28/shoes-chicco-sandalii/', (True, True)),
        ('/p/ra084agldh72/shoes-ralfringer-sapogi/', (True, True)),
        ('/men-home/', (False, False))
    ]
    general_test(domain_url, tests)


def ecco_shoes_test():
    domain_url = 'https://www.ecco-shoes.ru/'
    tests = [
        ('/accessories/', (False, False)),
        # ('/catalog/723733/50721/', (True, True)), # can't do anything with no "Обувь" in children's breadcrumbs.
        ('/catalog/634504/01053/', (True, True)),
        ('/men/shoes/classic/', (False, True))
        ]
    general_test(domain_url, tests)

def topshop_test():
    domain_url = 'http://www.top-shop.ru'
    tests = [
        ('/', (False, False)),
        ('/product/516637-almi-rim/', (True, True)),
        ('/product/434878-walkmaxx-running-shoes-2-0/', (True, True)),
        ('/genre/1652-krossovki/', (False, True)),
        ('/product/995922-grace-zhanna-cvet-zelenyy/', (True, False))
    ]
    general_test(domain_url, tests)

if __name__ == '__main__':
    bonprix_test()
    respect_shoes_test()
    antoniobiaggi_test()
    lamoda_test()
    ecco_shoes_test()
    topshop_test()
