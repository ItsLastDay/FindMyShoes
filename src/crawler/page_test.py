from page import Page

for s in [
    'http://www.ozon.ru/context/shoes/',
    'http://www.ozon.ru/context/shoes',
    'https://www.lamoda.ru/1',
    'https://www.lamoda.ru/',
]:
    p = Page(s)
    condition = p.url() == s
    if not condition:
        print("p.url(): '{}' not equal to string: '{}'".format(p.url(), s))
    assert condition
