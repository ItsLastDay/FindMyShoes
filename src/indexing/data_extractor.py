#!/usr/bin/env python3
import sys
import pathlib
import collections

import argparse
from multiprocessing import Pool
from functools import partial
from math import inf

import json
import copy

import urllib.parse

from extract import get_extractor_for_domain

count_by_domain = collections.Counter()


def get_page_domain(page_url):
    return urllib.parse.urlparse(page_url).netloc


def populate_data(data_dict, html_path, domain):
    """Extract all interesting data from page, save it to `data_dict`.
    """
    # It is crucial to read HTML *only if* we really need to. 
    # Otherwise, data extractor is slooow.
    raw_html = html_path.open().read()
    get_extractor_for_domain(domain).parse_html(raw_html, data_dict)


def extract_and_write_json(meta_file, json_dir, limit_by_domain=inf):
    """Given meta-information file about page, extract and store all interesting data from it.
    """
    # Example info: 
    # {'hash': 'a4da8866c9bb2fabe5abfda701a6e8ac',
    # 'url': 'https://www.bonprix.ru/produkty/tufli-krasnyj-971149/',
    # 'path': '_produkty##tufli-krasnyj-971149##', 'size': 612326}
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
        result_path = pathlib.Path(json_dir) / ('{}_{}_{}.json'.format(domain, meta_info['path'], meta_info['hash']))
        with result_path.open('w') as out:
            json.dump(result_dict, out, ensure_ascii=False)


def main():
    from common import default_raw_dir, default_json_dir
    parser = argparse.ArgumentParser(description="data_extractor")
    parser.add_argument("--domain-limit", type=int, default=inf)
    parser.add_argument("--json-dir", type=str, default=default_json_dir())
    parser.add_argument("--raw-dir", type=str, default=default_raw_dir())
    args = parser.parse_args()

    with Pool() as pool:
        meta_files = list(pathlib.Path(args.raw_dir).glob('**/*.meta'))
        file_task = partial(extract_and_write_json, json_dir=args.json_dir, limit_by_domain=args.domain_limit)
        pool.map(file_task, meta_files)

    return 0


if __name__ == '__main__':
    sys.exit(main())
