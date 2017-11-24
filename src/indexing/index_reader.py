#!/usr/bin/env python3

import json
import argparse

import struct
import mmap

import sys
from typing import Optional
from logging import getLogger
logger = getLogger("index_reader")

from index_builder import INVERTED_ENTRY_SIZE
from text_utils import TextExtractor


class IndexReader:
    def __init__(self, inverted_index_path, dictionary_path):
        self.dictionary_path = dictionary_path
        self.inverted_index_path = inverted_index_path

    def __enter__(self):
        logger.debug("Reading inverted index from path: " + self.inverted_index_path)
        self._inv_idx_fd = open(self.inverted_index_path, 'r+b')
        self._inv_idx_mmap = mmap.mmap(self._inv_idx_fd.fileno(), 0)

        with open(self.dictionary_path, 'r') as dict_read:
            self._dictionary = json.load(dict_read)

        return self

    def __exit__(self, *args):
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

    def get_documents(self, word, preprocess=True):
        word_entry = self.get_word_entry(word, preprocess)
        return self._get_documents_for_word_entry(word_entry)

    def _get_documents_for_word_entry(self, word_entry):
        if word_entry is None:
            return []
        offset = word_entry['offset_inverted']
        df = word_entry['df']

        documents = []
        for i in range(df):
            cur_offset = offset + i * INVERTED_ENTRY_SIZE
            doc_idx = struct.unpack('i', self._inv_idx_mmap[cur_offset:cur_offset + INVERTED_ENTRY_SIZE])[0]
            documents.append(self._dictionary['documents'][doc_idx])
        return documents

    def _document_path_from_id(self, document_id: str):
        return


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
            print(reader.get_documents(word))


if __name__ == '__main__':
    sys.exit(main())
