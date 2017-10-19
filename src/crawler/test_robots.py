import logging

logging.basicConfig(filename='./logs/test_robots_debug.log', level=logging.DEBUG, filemode='w')

from robots import RobotsProvider
from page import Page

domain_pages = {
    "https://respect-shoes.ru": ([
        ("/search/map.php", True),
        ("/obuv_id462073", True)
    ]),
    "https://google.com":
        [
            ("/maps/reserve/partners", True),
            ("/?hl=", True),
            ("/?hl=123", True),
            ("/?hl=123&", False),
            ("/?hL=123&", False)  # /?
        ]
}

for domain_url in domain_pages:
    pages_results = domain_pages[domain_url]
    for page_path, expected in pages_results:
        page = Page(domain_url, page_path)
        result = RobotsProvider.can_be_crawled(page)

        if result != expected:
            verdict = "allowed" if expected else "disallowed"
            print("[FAIL] page {} expected to be {} on domain {}".format(page_path, verdict, domain_url))
        else:
            print("[OK]   page {}, domain {}: {}".format(page_path, domain_url, result))
