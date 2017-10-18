from robots import RobotsProvider

domain_pages = {
    "https://respect-shoes.ru": ([
        ("https://respect-shoes.ru/search/map.php", True),
        ("https://respect-shoes.ru/obuv_id462073", True)
    ]),
    "https://google.com":
        [
            ("https://www.google.com/maps/reserve/partners", True),
            ("https://www.google.com/?hl=", True),
            ("https://www.google.com/?hl=123", True),
            ("https://www.google.com/?hl=123&", False),
            ("https://www.google.com/?hL=123&", False)  # /?
        ]
}

for domain_url in domain_pages:
    pages_results = domain_pages[domain_url]
    for page_url, expected in pages_results:
        result = RobotsProvider.can_be_crawled(domain_url, page_url)

        if result != expected:
            verdict = "allowed" if expected else "disallowed"
            print("[FAIL] page {} expected to be {} on domain {}".format(page_url, verdict, domain_url))
        else:
            print("[OK]   page {}, domain {}: {}".format(page_url, domain_url, result))
