import re

from nltk.tokenize import toktok
from nltk.stem.snowball import RussianStemmer


class TextExtractor:
    tokenizer = toktok.ToktokTokenizer()

    # Sentence is something that ends with '.', '!' or '?'
    sentence_splitter = re.compile('\.+|!+|\?+')

    # Good words are those that:
    #   - contain at least one letter (e.g. "какой-никакой", "10.5см")
    #   - consist entirely of digits (e.g. "38")
    # This filter is not aggressive on purpose.
    word_filter = re.compile(r'\w|^\d+$')

    stopwords = [
        'на',
        'и',
        'в',
        'не',
        'очень',
        'но',
        'с',
        'как',
        'для',
        'по',
        'обувь',
        'а',
        'из',
        'от',
        'без',
        'у',
        'к',
        'что'
    ]

    # stemming reference: http://snowball.tartarus.org/algorithms/russian/stemmer.html
    stemmer = RussianStemmer()

    @staticmethod
    def _split_by_sentences(text):
        return re.split(TextExtractor.sentence_splitter, text)

    @staticmethod
    def tokenize_sentence(sent):
        return TextExtractor.tokenizer.tokenize(sent)

    @staticmethod
    def get_normal_words_from_text(text: str) -> [str]:
        sentences = TextExtractor._split_by_sentences(text)
        words = []
        for sent in sentences:
            cur_words = TextExtractor.tokenize_sentence(sent)
            words.extend(cur_words)

        words = filter(TextExtractor.word_filter.match, words)
        words = map(lambda x: x.lower(), words)

        # removing stopwords.
        words = filter(lambda word: word not in TextExtractor.stopwords, words)

        # not making stem forms unique.
        words = map(TextExtractor.stemmer.stem, words)

        return list(words)

    @staticmethod
    def test():
        text = 'Я "поШЛА" ГулЯТЬ!!!! Как, и И всё??? И всё. 38 попугаев. 10 см. обувь лучшая. Guns and roses'
        sentences = TextExtractor._split_by_sentences(text)

        print(sentences)

        for sent in sentences:
            print(TextExtractor.tokenizer.tokenize(sent))

        print(TextExtractor.get_normal_words_from_text(text))


if __name__ == '__main__':
    TextExtractor.test()
