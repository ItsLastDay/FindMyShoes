#!/usr/bin/env python3

import json

import struct
import mmap

import sys

from index_builder import INVERTED_INDEX_PATH, INVERTED_ENTRY_SIZE, DICTIONARY_PATH

class IndexReader:
    def __enter__(self):
        print(INVERTED_INDEX_PATH)
        self._inv_idx_fd = open(INVERTED_INDEX_PATH, 'r+b')
        self._inv_idx_mmap = mmap.mmap(self._inv_idx_fd.fileno(), 0)

        with open(DICTIONARY_PATH, 'r') as dict_read:
            self._dictionary = json.load(dict_read)

        return self

    def __exit__(self, *args):
        self._inv_idx_mmap.close()
        self._inv_idx_fd.close()

    def get_documents(self, word):
        if word not in self._dictionary['words']:
            return []

        offset = self._dictionary['words'][word]['offset_inverted']
        df = self._dictionary['words'][word]['df']

        documents = []
        for i in range(df):
            cur_offset = offset + i * INVERTED_ENTRY_SIZE
            doc_idx = struct.unpack('i', self._inv_idx_mmap[cur_offset:cur_offset + INVERTED_ENTRY_SIZE])[0]
            documents.append(self._dictionary['documents'][doc_idx])

        return documents


def main():
    print('Демонстрация работы индекса. Вводите слова, получаете список документов, в которых слово встречается')

    with IndexReader() as reader:
        while True:
            word = input('Введите слово для поиска: ')
            print(reader.get_documents(word))


if __name__ == '__main__':
    sys.exit(main())
