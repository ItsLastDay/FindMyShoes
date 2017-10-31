#!/usr/bin/env python3
import sys
import os
import os.path
import pathlib

import json
import copy

import urllib.parse


from domain_specific_extractor import get_extractor_for_domain


DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, 'data'))

RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
JSON_DIR = os.path.join(DATA_DIR, 'json')


def get_page_domain(page_url):
    return urllib.parse.urlparse(page_url).netloc    


def populate_data(data_dict, raw_html, page_url):
    """Extract all interesting data from page, save it to `data_dict`.
    """
    domain = get_page_domain(page_url)
    get_extractor_for_domain(domain).parse_html(raw_html, data_dict)


def extract_and_write_json(meta_file):
    """Given meta-information file about page, extract and store all interesting data from it.
    """
    # Example info: 
    # {'hash': 'a4da8866c9bb2fabe5abfda701a6e8ac', 'url': 'https://www.bonprix.ru/produkty/tufli-krasnyj-971149/', 'path': '_produkty##tufli-krasnyj-971149##', 'size': 612326}
    meta_info = json.load(meta_file.open())

    html_path = meta_file.parent / (meta_info['path'] + '.html')
    raw_html = html_path.open().read()

    result_dict = copy.copy(meta_info)
    del result_dict['path']
    populate_data(result_dict, raw_html, meta_info['url'])


    result_path = pathlib.Path(JSON_DIR) / ('{}_{}.json'.format(meta_info['path'], meta_info['hash'])
    json.dump(result_dict, result_path)


def main():
    for meta_file in pathlib.Path(RAW_DATA_DIR).glob('**/*.meta'):
        extract_and_write_json(meta_file)

    return 0

if __name__ == '__main__':
    sys.exit(main())
