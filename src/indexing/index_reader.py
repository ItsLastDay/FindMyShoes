#!/usr/bin/env python3

import json
import argparse

import struct
import mmap

import sys
from typing import Optional
from logging import getLogger
logger = getLogger("index_reader")

from index_builder import INVERTED_ENTRY_SIZE, DocumentEntry
from text_utils import TextExtractor


class IndexReader:
    def __init__(self, inverted_index_path, weight_path, dictionary_path):
        self.dictionary_path = dictionary_path
        self.inverted_index_path = inverted_index_path
        self.weight_path = weight_path

    def __enter__(self):
        logger.debug("Reading inverted index from path: " + self.inverted_index_path)
        self._inv_idx_fd = open(self.inverted_index_path, 'r+b')
        self._inv_idx_mmap = mmap.mmap(self._inv_idx_fd.fileno(), 0)
        logger.debug("Reading weights from path: " + self.weight_path)
        self._weight_fd = open(self.weight_path, 'r+b')
        self._weight_mmap = mmap.mmap(self._weight_fd.fileno(), 0)

        logger.debug("Reading dictionary from path: " + self.dictionary_path)
        with open(self.dictionary_path, 'r') as dict_read:
            self._dictionary = json.load(dict_read)
        self._dictionary['documents'] = list(map(lambda doc_dict: DocumentEntry(**doc_dict), self._dictionary['documents']))
        return self

    def __exit__(self, *args):
        self._weight_mmap.close()
        self._weight_fd.close()
        self._inv_idx_mmap.close()
        self._inv_idx_fd.close()

    def get_word_entry(self, word, preprocess=True) -> Optional[dict]:
        # Apply same normalization as for computing index.
        if preprocess:
            word = TextExtractor.get_normal_words_from_text(word)
            word = None if not word else word[0]
        if word not in self._dictionary['words']:
            return None
        return self._dictionary['words'][word]

    def _get_documents_weights_for_word_entry(self, word_entry):
        if word_entry is None:
            return []
        offset = word_entry['offset_inverted']
        df = word_entry['df']

        documents = []
        for i in range(df):
            cur_offset = offset + i * INVERTED_ENTRY_SIZE
            doc_idx = struct.unpack('i', self._inv_idx_mmap[cur_offset:cur_offset + INVERTED_ENTRY_SIZE])[0]
            weight = struct.unpack('i', self._weight_mmap[cur_offset:cur_offset + INVERTED_ENTRY_SIZE])[0]
            next_doc = self._dictionary['documents'][doc_idx]
            documents.append((next_doc, weight))
        return documents

    def get_documents_weights(self, word, preprocess=True):
        word_entry = self.get_word_entry(word, preprocess)
        return self._get_documents_weights_for_word_entry(word_entry)


def main():
    from os.path import join
    from common import default_index_dir
    parser = argparse.ArgumentParser(description='Демонстрация работы индекса.\n'
                                                 'Вводите слова, получаете список документов, в которых слово встречается')
    parser.add_argument("-i", "--inverted-index-path", type=str, default=join(default_index_dir(), 'inverted.bin'))
    parser.add_argument("-d", "--dictionary", type=str, default=join(default_index_dir(), 'dictionary.txt'))
    args = parser.parse_args()

    with IndexReader(inverted_index_path=args.inverted_index_path, dictionary_path=args.dictionary) as reader:
        while True:
            word = input('Введите слово для поиска: ')
            documents_weights = reader.get_documents_weights(word)
            print('\n'.join(map(lambda doc_weight: doc_weight[0].path, documents_weights)))


if __name__ == '__main__':
    sys.exit(main())
