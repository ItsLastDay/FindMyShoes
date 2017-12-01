from logging import getLogger
from extract.abstract import extractor_for, AbstractDataExtractor, JSONKey

logger = getLogger('kinderly_extract')

@extractor_for('www.kinderly.ru')
class KinderlyExtractor(AbstractDataExtractor):
    # Examples:
    #   www.kinderly.ru/product/zebra-12027-1-sapogi-shkolnye-uteplennye-12-par-v-kor

    _NAME_SELECTOR = 'h1.product-full__title'
    _BRAND_SELECTOR = 'ul.product-full__meta-list > li:nth-child(1) > span > a '
    _TYPE_SELECTOR = 'div.breadcrumb > ul > li:nth-child(3) > a > span'
    _PRICE_SELECTOR = 'span.product-full-actions__price'
    _SIZES_SELECTOR = 'label.change-size > span'

    _GENDER_SELECTOR = 'div.product-full__characteristics > ul > li:nth-last-child(1) > div > a'
    _IMG_SELECTOR = 'div.product-full__images-small > span'

    _DESCRIPTION_SELECTOR = 'article[class="product-full__description static-content"] > p > span' # several spans!!!
    _REVIEWS_SELECTOR = 'div.product-full-review__content > p > span' # top-level reviews only.

    _ATTRIBUTE_NAMES_SELECTOR = 'div.product-full__characteristics-list-item-left'
    _ATTRIBUTE_VALUES_SELECTOR = 'div.product-full__characteristics-list-item-right > span'

    def _parse_name(self):
        data = self._get_data_by_selector(self._NAME_SELECTOR)
        if data:
            name = data[0]
            pos = name.find('(')
            if pos != -1:
                name = name[:pos]
            self._save_raw(JSONKey.NAME_KEY, name)

    def _parse_colors(self):
        data = self._get_data_by_selector(self._NAME_SELECTOR)
        if data:
            name = data[0]
            if name.find('(') != -1 and name[-1] == ')':
                colors = name.split('(')[1][:-1].split(',')
                self._save_raw(JSONKey.COLORS_KEY, colors)

    # def _parse_sizes(self):
    #     ul = [0]
    #     for label in self._selectable_data.cssselect(self._SIZES_SELECTOR):
    #         # FIXME on disabled sizes label has children <input> with property disabled="disabled".
    #         # input = label.find('input') now returns None.
    #         span = label.find('span')
    #         if span is not None and span.text.isdigit():

    def _parse_description(self):
        spans = self._get_data_by_selector(self._DESCRIPTION_SELECTOR)
        self._save_raw(JSONKey.DESCRIPTION_KEY, ' '.join(spans))
