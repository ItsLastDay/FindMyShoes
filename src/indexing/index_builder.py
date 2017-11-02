#!/usr/bin/env python3

import pathlib
import collections
import argparse

import json
import struct

import sys
import mmap

from text_utils import TextExtractor

# Store entries in inverted index as integers.
INVERTED_ENTRY_SIZE = struct.calcsize('i')


def get_words_from_path(doc_path):
    json_data = None
    with doc_path.open() as f:
        json_data = json.load(f)

    product_description = '{}\n{}'.format(json_data.get('description', ''), 
                                          '\n'.join(json_data.get('reviews', '')))
    return TextExtractor.get_normal_words_from_text(product_description)


def make_first_pass(documents):
    """First pass of indexation: count word occurencies and required index size.

    Returns dictionary of the following form:
    {
        documents: [json_name_of_doc1, json_name_of_doc2, ..., json_name_of_docn]
        words: {
            'азбука': {
                'global_count': 12345       --- total number of occurencies in corpus
                'df': 67                    --- document frequency
                'offset_inverted': 98       --- offset (in bytes) of word's inverted index in global inverted index
                'offset_weight': 1023       --- same as above, but in global weights index
            }
            'машина': { ... }
            ...
        }
    }
    """
    result_dict = dict()

    result_dict['documents'] = list(map(lambda path: path.name, documents))
    words_dict = dict()
    result_dict['words'] = words_dict

    for i, doc in enumerate(documents):
        print('Reading document {}'.format(i))
        words = get_words_from_path(doc)

        added_df_words = set()
        for word in words:
            if word not in words_dict:
                words_dict[word] = dict(global_count=0, df=0, offset_inverted=0, offset_weight=0)

            words_dict[word]['global_count'] += 1
            if word not in added_df_words:
                words_dict[word]['df'] += 1
                added_df_words.add(word)

    print('Scanned all documents')

    current_offset = 0
    for word in words_dict:
        words_dict[word]['offset_inverted'] = current_offset
        words_dict[word]['offset_weight'] = current_offset
        current_offset += INVERTED_ENTRY_SIZE * words_dict[word]['global_count']

    print('First pass finished')

    return result_dict


def make_second_pass_inner(weights, inverted, documents, dictionary):
    current_write_position = dict()
    for word in dictionary['words']:
        current_write_position[word] = dictionary['words'][word]['offset_inverted']

    for i, doc in enumerate(documents):
        words = get_words_from_path(doc)
        tf = collections.Counter(words)

        # Write document id in inverted list, term frequency to weights list.
        for word in set(words):
            cur_offs = current_write_position[word]

            weights[cur_offs:cur_offs + INVERTED_ENTRY_SIZE] = struct.pack('i', tf[word])
            inverted[cur_offs:cur_offs + INVERTED_ENTRY_SIZE] = struct.pack('i', i)

            current_write_position[word] += INVERTED_ENTRY_SIZE

    print('Second pass finished')


def make_second_pass(documents, dictionary, inverted_index_path, weight_path):
    """Second pass of indexation: actually store data to index.
    """
    word_freq_pairs = [(word, dictionary['words'][word]['global_count']) for word in dictionary['words']]
    word_freq_pairs = sorted(word_freq_pairs, key=lambda x: x[1], reverse=True)
    index_size = sum(map(lambda x: x[1], word_freq_pairs)) * INVERTED_ENTRY_SIZE

    print('Required index size {} bytes'.format(index_size))
    print('Top 30 words: {}'.format(word_freq_pairs[:30]))

    with open(inverted_index_path, 'w+b') as inverted_index:
        with open(weight_path, 'w+b') as weight_index:
            inverted_index.write(b'\0' * index_size)
            weight_index.write(b'\0' * index_size)
            with mmap.mmap(weight_index.fileno(), index_size) as weight_mmap:
                with mmap.mmap(inverted_index.fileno(), index_size) as inverted_mmap:
                    make_second_pass_inner(weight_mmap, inverted_mmap, documents, dictionary)


def main():
    from os.path import join
    from common import default_index_dir, default_json_dir

    parser = argparse.ArgumentParser(description="Index builder.")
    parser.add_argument("--json-dir", type=str, default=default_json_dir())
    parser.add_argument("--index-dir", type=str, default=default_index_dir())

    # TODO distinguish between input and output arguments:
    # add parsing group, for instance.
    parser.add_argument("-i", "--inverted-index-path", type=str, default=join(default_index_dir(), 'inverted.bin'))
    parser.add_argument("-w", "--weight-path", type=str, default=join(default_index_dir(), 'weight.bin'))
    parser.add_argument("-d", "--dictionary", type=str, default=join(default_index_dir(), 'dictionary.txt'))

    args = parser.parse_args()

    documents = list(pathlib.Path(args.json_dir).glob('*.json'))
    dictionary = make_first_pass(documents)
    make_second_pass(documents, dictionary, inverted_index_path=args.inverted_index_path, weight_path=args.weight_path)

    with open(args.dictionary, 'w') as dict_out:
        json.dump(dictionary, dict_out, ensure_ascii=False)

    return 0


if __name__ == '__main__':
    sys.exit(main())
