from robots import RobotsProvider

# domain_url = "http://google.com"
# pages = [
#     "https://www.google.com/maps/reserve/partners",
#     "123"
# ]

domain_url = "https://respect-shoes.ru"
pages = [
    "https://respect-shoes.ru/search/map.php",
    "123"
]

expected_result = [True, False]
for page_url, expected in zip(pages, expected_result):
    result = RobotsProvider.can_be_crawled(domain_url, page_url)
    print(page_url, result)
    assert result == expected