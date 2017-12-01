from logging import getLogger
from extract.abstract import extractor_for, AbstractDataExtractor, JSONKey

logger = getLogger('kctati_extract')

# https://kctati.ru/catalog/botforty/botforty_ascalini_11/

@extractor_for('kctati.ru')
class KctatiExtractor(AbstractDataExtractor):
    # Examples:
    #   https://kctati.ru/catalog/botilony/botilony_cupage_11/

    _NAME_SELECTOR = 'div.dop_info > p'
    _BRAND_SELECTOR = 'ul[class="display_properties lsnn"] > li:nth-child(2) > span.opt_val'
    _TYPE_SELECTOR = 'ul[class="display_properties lsnn"] > li:nth-child(11) > span.opt_val'
    _COLORS_SELECTOR = 'ul[class="display_properties lsnn"] > li:nth-child(9) > span.opt_val'
    _SIZES_SELECTOR = 'div#new_SIZE > div > span > label' # FIXME uses js, doesn't work.
    _GENDER_SELECTOR = 'ul[class="breadcrumb-navigation red"] > li:nth-child(5) span'
    _IMG_SELECTOR = 'img#detail_picture'

    _DESCRIPTION_SELECTOR = 'ul[class="product_info df"] > li:nth-last-child(1)'

    _ATTRIBUTE_NAMES_SELECTOR = 'ul[class="display_properties lsnn"] > li > span:nth-child(1)'
    _ATTRIBUTE_VALUES_SELECTOR = 'ul[class="display_properties lsnn"] > li > span.opt_val'

    # TODO reviews (not found any examples).

    def _parse_price(self):
        data = self._get_data_by_selector('div.discount-price') # div.old_price
        if data is None or len(data) == 0:
            data = self._get_data_by_selector('div.price')
        if data:
            self._save_raw(JSONKey.PRICE_KEY, AbstractDataExtractor.price_from_string(data))

    def _parse_attributes(self):
        attributes = dict()
        names = self._get_data_by_selector(self._ATTRIBUTE_NAMES_SELECTOR)
        values_tags = self._selectable_data.cssselect(self._ATTRIBUTE_VALUES_SELECTOR)
        if len(values_tags) != len(names):
            logger.warning('len(values_tags) != len(names)')
            return
        for name, value_tag in zip(names, values_tags):
            aa = value_tag.find('a')
            if aa is None:
                attributes[name] = value_tag.text
            else:
                attributes[name] = aa.text

        self._save_raw(JSONKey.ATTRIBUTES_KEY, attributes)
