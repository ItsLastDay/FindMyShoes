from extract.abstract import extractor_for, AbstractDataExtractor, JSONKey

@extractor_for('www.lamoda.ru')
class LamodaExtractor(AbstractDataExtractor):
    # Examples:
    #    https://www.lamoda.ru/p/lo019awgvm60/shoes-lostink-bosonozhki/
    #    https://www.lamoda.ru/p/oo001awkvi31/shoes-oodji-baletki/

    _BRAND_SELECTOR = 'a.ii-product__brand-text'
    _NAME_SELECTOR = 'h1.ii-product__title'
    _GENDER_SELECTOR = 'div.breadcrumbs span:nth-child(2) span'
    _TYPE_SELECTOR = 'div.breadcrumbs span:nth-last-child(1) span'
    _SIZES_SELECTOR = 'div.ii-select__columns > div.ii-select__column_native > div.ii-select__option'
    _PRICE_SELECTOR = 'div.ii-product__price-current'

    _ATTRIBUTE_NAMES_SELECTOR = 'div.ii-product__attributes > div > span.ii-product__attribute-label'
    _ATTRIBUTE_VALUES_SELECTOR = 'div.ii-product__attributes > div > span.ii-product__attribute-value'
    _DESCRIPTION_SELECTOR = 'div.ii-product__description-text > div[itemprop=description]'
    _REVIEWS_SELECTOR = 'div.rev__node_review > div.rev__node-body[itemprop=description]'

    def _parse_sizes(self):
        def process_size(s: str) -> float:
            float_str = s.replace(',', '.').split(' ')[0]
            if '/' in float_str:
                a, b = tuple(map(int, float_str.split('/')))
                return (a + b) / 2
            return float(float_str)

        def process_sizes(sizes: [str]):
            rus_sizes = filter(lambda s: 'RUS' in s, sizes)
            return list(map(process_size, rus_sizes))
        self._save(JSONKey.SIZES_KEY, self._SIZES_SELECTOR, process_sizes)