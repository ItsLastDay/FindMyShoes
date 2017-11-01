import re
import string

from nltk.tokenize import toktok


tokenizer = toktok.ToktokTokenizer()

# Sentence is something that ends with '.', '!' or '?'
sent_splitter = re.compile('\.+|!+|\?+')


def split_by_sentences(text):
    return re.split(sent_splitter, text)

def tokenize_sentence(sent):
    return tokenizer.tokenize(sent)

def get_normal_words_form_text(text):
    sentences = split_by_sentences(text)
    words = []
    for sent in sentences:
        cur_words = tokenize_sentence(sent)
        words.extend(cur_words)

    # Erase all words that do not contain letter
    words = filter(lambda x: re.match('\w', x), words)
    words = map(lambda x: x.lower(), words)

    # TODO: stemming
    # TODO: stopword removal

    return list(words)


def test():
    text = 'Я поШЛА ГулЯТЬ!!!! Как, и И всё??? И всё.'
    sents = split_by_sentences(text)

    print(sents)

    for sent in sents:
        print(tokenizer.tokenize(sent))

    print(get_normal_words_form_text(text))

if __name__ == '__main__':
    test()
