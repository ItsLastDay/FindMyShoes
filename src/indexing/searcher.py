#!/usr/bin/env python3
import argparse
import logging
from logging import getLogger
from collections import defaultdict
import math

from pymongo import MongoClient
import os.path

logger = getLogger('searcher')

from index_reader import IndexReader
from index_builder import IndexBuilder
from text_utils import TextExtractor
from index_builder import DocumentEntry


def make_colors_dict(color_set: [str]):
    res = dict()
    for color in color_set:
        res[TextExtractor.stem(color)] = color
    return res


class DocumentRank:
    def __init__(self, doc, rank):
        self._doc = doc
        self._rank = rank

    def __eq__(self, other: 'DocumentRank'):
        return self._rank == other._rank and self.site == other.site

    def __hash__(self):
        return hash(self._rank) ^ hash(self.site)

    def get(self):
        return self._doc, self._rank

    @property
    def site(self):
        path = self._doc.path
        i = path.find('__')
        return path[:i]


class QueryProcessor:
    IDF_SMOOTH = 0.5

    def __init__(self, index_reader: IndexReader, json_dir: str):
        self._index_reader = index_reader
        self._dictionary = index_reader._dictionary
        self._documents = self._dictionary.get('documents')
        self._k1 = 2.0
        self._b = 0.75
        self._json_dir = json_dir

        self._db_client = MongoClient('localhost', 27017)
        # Using data imported by `database_storer.sh`.
        self._db = self._db_client.findmyshoes
        self._db_docs = self._db.data

        dbcolors = self._db_docs.aggregate([
            {'$unwind': {'path': '$colors'}},
            {'$project': {'_id': 0, 'colors': 1}},
            {'$group': {
                '_id': "$colors",
                'count': {'$sum': 1}
            }
            },
            {'$sort': {"count": -1}}
        ]
        )

        def extract_hues(color_count):
            if color_count['count'] > 10:
                return []
            raw = color_count['_id'].lower().strip().replace('ё', 'е')
            for hue in ['темно-', 'светло-']:
                if raw.startswith(hue):
                    raw = raw[len(hue):]
            hues = raw.split('/')
            return list(filter(lambda hue: len(hue) > 0 and len(hue.split(' ')) == 1, hues))

        hues = sum(list(map(extract_hues, dbcolors)), [])
        colors = set(hues)
        self._colors = make_colors_dict(colors)

    def preprocess(self, query: str) -> [str]:
        """
        :param query string from user
        :return list of terms
        """
        words = TextExtractor.get_normal_words_from_text(query)
        return words

    def bm25_score(self, doc: DocumentEntry, terms: [str], weights: [float]) -> (str, float):
        """
        :param doc: document_id
        :param terms: list of stemmed terms.
        :param weights: list of frequencies of corresponding terms in doc.
        :return: Okapi BM25-score: https://ru.wikipedia.org/wiki/Okapi_BM25
        """

        assert len(terms) == len(weights)
        ndocs = len(self._documents)
        avgdl = self._dictionary.get('avgdl')

        assert len(terms) == len(set(terms))
        # logger.debug('BM25-scoring document {}'.format(doc.path))
        score = 0
        for term, fqd in zip(terms, weights):
            # term in document frequency
            word_entry = self._index_reader.get_word_entry(term, False)
            if word_entry is None or fqd == 0: continue
            df = word_entry.get('df')
            idf = math.log2((ndocs - df + QueryProcessor.IDF_SMOOTH) / (df + QueryProcessor.IDF_SMOOTH))
            score += idf * fqd * (self._k1 + 1) / (fqd + self._k1 * (1 - self._b + self._b * doc.length / avgdl))
        return doc, score

    # TODO implement passing projection.
    def dbfind(self, command, projection={"_id": 0}):
        projection_parameter = {}
        projection_parameter.update(projection)
        return self._db_docs.find(command, projection_parameter)

    def get_urls_match_size(self, desired_size):
        # `desired_size` - shoes size, integer between 24 and 50.

        # https://stackoverflow.com/a/18148872/5338270
        # TODO fix as we now store sizes in float, make search less strict.
        return list(map(lambda x: x['url'], self.dbfind({'sizes': desired_size})))

    def get_urls_match_color(self, color):
        # TODO use stemming (or better mongo text search) on color names.
        return list(map(lambda x: x['url'], self.dbfind({'colors': color})))

    def ranked_documents(self, terms: [str]) -> [str, float]:
        for term in terms:
            if self._index_reader.get_word_entry(term) is None:
                logger.warning("term {} not found in collection".format(term))
        match_docs_weights = defaultdict(lambda: [None, [0] * len(terms)])
        logger.debug("Searching any match documents")
        for i, term in enumerate(terms):
            term_docs_weights = self._index_reader.get_documents_weights(term, False)
            for doc, weight in term_docs_weights:
                match_docs_weights[doc.url][1][i] = weight
                match_docs_weights[doc.url][0] = doc
        logger.debug("Any match documents found: %d" % len(match_docs_weights))
        document_ranks = [self.bm25_score(doc, terms, weights) for doc, weights in match_docs_weights.values()]
        return document_ranks

    def filtered_documents(self, terms, ranked_docs):
        good_urls = set(map(lambda x: x[0].url, ranked_docs))

        # Filter by size. If integer between 24 and 50 is found
        # in query, it is considered the desired shoe size (what else it could be?)
        for term in terms:
            try:
                size = float(term)
                if 24 <= size <= 50:
                    good_urls &= set(self.get_urls_match_size(size))
                    # print(good_urls)
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
            if ranked_docs[i][0].url in boosted_urls:# and 'ozon' not in ranked_docs[i][0].url:
                ranked_docs[i] = (ranked_docs[i][0], ranked_docs[i][1] * 2)
        return list(filter(lambda x: x[0].url in good_urls, ranked_docs))

    def unique_documents(selfs, ranked_docs):
        s = set(map(lambda dr: DocumentRank(*dr), ranked_docs))
        return list(map(lambda dr: dr.get(), s))

    def get_coincidence_string(self, doc: DocumentEntry, terms: [str], neighbors=2) -> str:
        objects = list(self.dbfind({'url': doc.url}))
        if len(objects) == 0:
            return ""
        json_data = objects[0]
        # FIXME bad architecture!!!
        words = IndexBuilder._get_words_from_json(json_data, False)
        n = len(words)
        highlights = [False] * n
        saved = [False] * n
        for i, w in enumerate(words):
            wstem = TextExtractor.stem(w)
            if any(map(lambda t: wstem == TextExtractor.stem(t), terms)):
                highlights[i] = True
                for j in range(max(0, i - neighbors), min(i + neighbors + 1, n - 1)):
                    saved[j] = True
        return ' '.join('<b>{}</b>'.format(w) if h else w for w, h, s in zip(words, highlights, saved) if s)

    def get_ranked_docs(self, query_string, page=1, limit=10):
        terms = self.preprocess(query_string)
        documents_ranks = self.ranked_documents(terms)
        filtered_docs = self.filtered_documents(terms, documents_ranks)
        unique_documents = self.unique_documents(filtered_docs)
        n = len(unique_documents)
        start = (page - 1) * limit
        stop = page * limit
        best_documents_ranks = sorted(unique_documents,
                                      key=lambda dr: dr[1], reverse=True)[start:stop]
        best_documents_coincidence = [self.get_coincidence_string(dr[0], terms) for dr in best_documents_ranks]
        return n, best_documents_ranks, best_documents_coincidence


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    from common import default_index_dir, default_json_dir

    parser = argparse.ArgumentParser(description='Демонстрация работы индекса.\n'
                                                 'Вводите слова, получаете список документов, в которых слово встречается')
    parser.add_argument("-i", "--inverted-index-path", type=str,
                        default=os.path.join(default_index_dir(), 'inverted.bin'))
    parser.add_argument("-w", "--weight-path", type=str, default=os.path.join(default_index_dir(), 'weight.bin'))
    parser.add_argument("-d", "--dictionary", type=str, default=os.path.join(default_index_dir(), 'dictionary.txt'))
    parser.add_argument("--json-dir", type=str, default=default_json_dir())
    args = parser.parse_args()

    with IndexReader(args.inverted_index_path, args.weight_path, args.dictionary) as index_reader:
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
            filtered_docs = query_processor.filtered_documents(terms, documents_ranks)
            logger.debug("Documents after filtering: {}".format(len(filtered_docs)))
            best_documents_ranks = sorted(filtered_docs, key=lambda dr: dr[1], reverse=True)[:limit]
            logger.info(
                "Best options: {}".format(list((url_from_json(doc), rank) for doc, rank in best_documents_ranks)))
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
