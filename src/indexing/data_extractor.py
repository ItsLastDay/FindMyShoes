#!/usr/bin/env python3
import sys
import os
import os.path
import pathlib

import collections

from multiprocessing import Pool

import json
import copy

import urllib.parse


from domain_specific_extractor import get_extractor_for_domain


DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, 'data'))

RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
JSON_DIR = os.path.join(DATA_DIR, 'json')

count_by_domain = collections.Counter()
limit_by_domain = 10 ** 9


def get_page_domain(page_url):
    return urllib.parse.urlparse(page_url).netloc    


def populate_data(data_dict, html_path, domain):
    """Extract all interesting data from page, save it to `data_dict`.
    """
    # It is crucial to read HTML *only if* we really need to. 
    # Otherwise, data extractor is slooow.
    raw_html = html_path.open().read()
    get_extractor_for_domain(domain).parse_html(raw_html, data_dict)


def extract_and_write_json(meta_file):
    """Given meta-information file about page, extract and store all interesting data from it.
    """
    # Example info: 
    # {'hash': 'a4da8866c9bb2fabe5abfda701a6e8ac', 'url': 'https://www.bonprix.ru/produkty/tufli-krasnyj-971149/', 'path': '_produkty##tufli-krasnyj-971149##', 'size': 612326}
    meta_info = None
    with meta_file.open() as f:
        meta_info = json.load(f)

    html_path = meta_file.parent / (meta_info['path'] + '.html')

    result_dict = copy.copy(meta_info)
    del result_dict['path']

    domain = get_page_domain(meta_info['url'])
    # Limit count of pages for debugging purposes.
    count_by_domain[domain] += 1
    if count_by_domain[domain] <= limit_by_domain:
        print(html_path)
        populate_data(result_dict, html_path, domain)
        result_path = pathlib.Path(JSON_DIR) / ('{}_{}_{}.json'.format(domain, meta_info['path'], meta_info['hash']))
        with result_path.open('w') as out:
            json.dump(result_dict, out, ensure_ascii=False)


def main():
    global limit_by_domain
    if len(sys.argv) > 1:
        limit_by_domain = int(sys.argv[1])

    with Pool() as pool:
        meta_files = list(pathlib.Path(RAW_DATA_DIR).glob('**/*.meta'))
        pool.map(extract_and_write_json, meta_files)

    return 0

if __name__ == '__main__':
    sys.exit(main())
