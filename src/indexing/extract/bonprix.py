from extract.abstract import extractor_for, AbstractDataExtractor, JSONKey

@extractor_for('www.bonprix.ru')
class BonprixExtractor(AbstractDataExtractor):
    # Examples:
    #    https://www.bonprix.ru/produkty/pantolety-iz-naturalnoj-kozhi-bezhevyj-919945/#image,
    #    https://www.bonprix.ru/produkty/kedy-bez-shnurkov-sinijbelyj-v-kletku-929840/#image

    _NAME_SELECTOR = 'div h1.product-name'
    _GENDER_SELECTOR = 'div#breadcrumb span:nth-child(3) span'
    _PRICE_SELECTOR = 'span.price-tag > span.integer-place'
    _COLORS_SELECTOR = 'span.product-information > span.product-display-name'
    _SIZES_SELECTOR = 'ul#product-variant-size a'

    _DESCRIPTION_SELECTOR_1 = 'p.product-information-full-description'
    _DESCRIPTION_SELECTOR_2 = 'section#product-info h2'
    _ATTRIBUTE_NAMES_SELECTOR = 'strong.product-attribute-name'
    _ATTRIBUTE_VALUES_SELECTOR = 'span.product-attribute-value'
    _REVIEWS_SELECTOR = 'p.reviewText'

    def _parse_description(self):
        desc1 = self._get_data_by_selector(self._DESCRIPTION_SELECTOR_1)
        desc2 = self._get_data_by_selector(self._DESCRIPTION_SELECTOR_2)
        self._save_raw(JSONKey.DESCRIPTION_KEY, '{}\n{}'.format(desc1, desc2))

    def _parse_sizes(self):
        data = self._get_raw_data_by_selector(self._SIZES_SELECTOR)
        if len(data) == 0:
            return
        # Example of .text_content(): "'\nНемецкий размер36\n\t"
        sizes = list(map(lambda x: x.text_content().strip()[-2:], data))
        if sizes:
            self._save_raw(JSONKey.SIZES_KEY, AbstractDataExtractor.process_sizes(sizes))

    def _parse_colors(self):
        texts = self._get_data_by_selector(self._COLORS_SELECTOR)
        texts = list(map(lambda text: text.replace('&nbsp', ''), texts))
        self._save_raw(JSONKey.COLORS_KEY, texts)
