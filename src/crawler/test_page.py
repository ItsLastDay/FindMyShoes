from page import Page
from bs4 import BeautifulSoup
from collections import namedtuple
import logging

logging.basicConfig(filename='./logs/test_page_debug.log', level=logging.DEBUG, filemode='w')

PageTestResult = namedtuple('PageTestResult', ['indexable', 'children'])

simple_html = """
<html>
<head>
<meta name="robots" CONTENT="nofollow">
</head>
<body>
</body>
</html>
"""

html_doc = """
<html>
<head>
<title>The Dormouse's story</title>
<META NAME="ROBOTS" CONTENT="NOINDEX">
</head>
<body>
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
</body>
</html>
"""

html_results = [
    (simple_html, PageTestResult(True, [])),
    (html_doc, PageTestResult(False, ['http://example.com/elsie',
                                      'http://example.com/lacie',
                                      'http://example.com/tillie']))
]

for i, (html_text, page_test_result) in enumerate(html_results):
    page = Page('http://example.com', '/index.html')
    page._soup = BeautifulSoup(html_text, 'lxml')
    page.modified()
    expected = "should be stored" if page_test_result.indexable else "should not be stored"
    if page.can_be_stored() != page_test_result.indexable:
        print("[FAIL] page #{} {}".format(i, expected))
    else:
        print("[ OK ] page #{} {}".format(i, expected))

    expected = "should be followed by {}".format(page_test_result.children)
    children_urls = list(map(lambda p: p.url(), page.children()))
    if children_urls != page_test_result.children:
        print("[FAIL] page #{} {} but has {}".format(i, expected, children_urls))
    else:
        print("[ OK ] page #{} {}".format(i, expected))
