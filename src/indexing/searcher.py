#!/usr/bin/env python3
import argparse
import logging
from logging import getLogger
from collections import namedtuple, defaultdict
from functools import partialmethod
import math
from pathlib import Path

import json
from text_utils import TextExtractor

from pymongo import MongoClient
import os.path

logger = getLogger('searcher')

from index_reader import IndexReader
from text_utils import TextExtractor
from index_builder import IndexBuilder


def make_colors_dict(colors):
    res = dict()
    for color in colors:
        res[TextExtractor.get_normal_words_from_text(color)[0]] = color

    return res


class QueryProcessor:
    IDF_SMOOTH = 0.5

    def __init__(self, index_reader: IndexReader, json_dir: str):
        self._index_reader = index_reader
        self._avgdl = index_reader._dictionary.get('avgdl')
        self._ndocs = len(index_reader._dictionary.get('documents'))
        self._k1 = 2.0
        self._b = 0.75
        self._json_dir = json_dir

        self._db_client = MongoClient('localhost', 27017)
        # Using data imported by `database_storer.sh`.
        self._db = self._db_client.findmyshoes
        self._db_docs = self._db.data

        self._colors = make_colors_dict([
            'белый', 
            'бордовый', 
            'чёрный', 'черный',
            'розовый'
            ])

    def preprocess(self, query: str) -> [str]:
        """
        :param query string from user
        :return list of terms
        """
        words = TextExtractor.get_normal_words_from_text(query)
        return words

    def bm25_score(self, doc, terms):
        """
        :param doc: document_id
        :param terms: list of stemmed terms.
        :return: Okapi BM25-score: https://ru.wikipedia.org/wiki/Okapi_BM25
        """
        assert len(terms) == len(set(terms))
        logger.debug('BM25-scoring document {}'.format(doc))
        doc_path = Path(os.path.join(self._json_dir, doc))
        doc_words = IndexBuilder._get_words_from_path(doc_path)
        score = 0
        for term in terms:
            # term in document frequency
            fqd = doc_words.count(term)
            word_entry = self._index_reader.get_word_entry(term)

            if word_entry is None: continue
            df = word_entry.get('df')
            idf = math.log2((self._ndocs - df + QueryProcessor.IDF_SMOOTH) / (df + QueryProcessor.IDF_SMOOTH))
            score += idf * fqd * (self._k1 + 1) / (fqd + self._k1 * (1 - self._b + self._b * len(doc_words) / self._avgdl))

        with doc_path.open() as doc:
            return json.load(doc)['url'], score

    def get_urls_match_size(self, desired_size):
        # `desired_size` - shoes size, integer between 24 and 50.

        # https://stackoverflow.com/a/18148872/5338270
        return list(map(lambda x: x['url'], self._db_docs.find({ 'sizes': str(desired_size) })))

    def get_urls_match_color(self, color):
        return list(map(lambda x: x['url'], self._db_docs.find({ 'colors': color })))

    def ranked_documents(self, terms: [str]) -> [str, float]:
        for term in terms:
            if self._index_reader.get_word_entry(term) is None:
                logger.warning("term {} not found in collection".format(term))
        match_docs = defaultdict(list)
        logger.debug("Searching any match documents")
        for term in terms:
            term_docs = self._index_reader.get_documents(term, False)
            for doc in term_docs:
                match_docs[doc].append(term)
        logger.debug("Any match documents found: %d" % len(match_docs))
        document_ranks = [self.bm25_score(doc, terms) for doc in match_docs]
        return document_ranks

    def filtered_documents(self, terms, ranked_docs):
        good_urls = set(map(lambda x: x[0], ranked_docs))

        # Filter by size. If integer between 24 and 50 is found
        # in query, it is considered the desired shoe size (what else it could be?)
        for term in terms:
            try:
                size = int(term)
                if 24 <= size <= 50:
                    good_urls &= set(self.get_urls_match_size(size))
            except ValueError:
                pass

        # Filter by color. Use dict of colors that can occur.
        # For each found term that is a color, boost ranking 
        # of documents that match this color.
        # We cannot simply drop documents that do not match,
        # because colors can be represented differently
        # on different sites (e.g. I saw "белый\чёрный" instead
        # of ["белый", "чёрный"]).
        boosted_urls = set()
        for term in terms:
            if term in self._colors:
                boosted_urls |= set(self.get_urls_match_color(self._colors[term]))

        for i in range(len(ranked_docs)):
            if ranked_docs[i][0] in boosted_urls:
                ranked_docs[i] = (ranked_docs[i][0], ranked_docs[i][1] * 2)


        return list(filter(lambda x: x[0] in good_urls, ranked_docs))

    def get_ranked_docs(self, query_string, limit=10):
        terms = self.preprocess(query_string)
        documents_ranks = self.ranked_documents(terms)
        filtered_docs = self.filtered_documents(terms, documents_ranks)
        best_documents_ranks = sorted(filtered_docs, key=lambda dr: dr[1], reverse=True)[:limit]
        return best_documents_ranks


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    from common import default_index_dir, default_json_dir
    parser = argparse.ArgumentParser(description='Демонстрация работы индекса.\n'
                                                 'Вводите слова, получаете список документов, в которых слово встречается')
    parser.add_argument("-i", "--inverted-index-path", type=str, default=os.path.join(default_index_dir(), 'inverted.bin'))
    parser.add_argument("-d", "--dictionary", type=str, default=os.path.join(default_index_dir(), 'dictionary.txt'))
    parser.add_argument("--json-dir", type=str, default=default_json_dir())
    args = parser.parse_args()

    with IndexReader(inverted_index_path=args.inverted_index_path, dictionary_path=args.dictionary) as index_reader:
        query_processor = QueryProcessor(index_reader, args.json_dir)
        logger.debug('shoes with 24 size:{}'.format(query_processor.get_urls_match_size(24)))
        def url_from_json(json_path):
            encoded_path = json_path[:json_path.rfind('##')]
            return encoded_path.replace('__', '/', 1).replace('##', '/')

        def process_query(query_string: str, limit=10):
            logger.debug("Processing query: " + query_string)
            terms = query_processor.preprocess(query_string)
            logger.debug("Extracted terms: " + str(terms))
            documents_ranks = query_processor.ranked_documents(terms)
            logger.debug("Documents found: {}".format(len(documents_ranks)))
            #logger.debug("Documents found: {}".format(documents_ranks))
            filtered_docs = query_processor.filtered_documents(terms, documents_ranks)
            logger.debug("Documents after filtering: {}".format(len(filtered_docs)))
            best_documents_ranks = sorted(filtered_docs, key=lambda dr: dr[1], reverse=True)[:limit]
            logger.info("Best options: {}".format(list((url_from_json(doc), rank) for doc, rank in best_documents_ranks)))
            return documents_ranks

        # process_query("сочные")
        # process_query("швы")
        # process_query("сочные швы")
        # process_query('24 балетки')
        # process_query('чёрные кеды')
        # process_query("балетки резина кожа олень")
        # process_query("удобные туфли от удовольствия")
        # process_query("детские балетки с перфорацией")
        while True:
            query_string = input('Введите запрос: ')
            process_query(query_string)
