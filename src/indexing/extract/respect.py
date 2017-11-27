from extract.abstract import extractor_for, AbstractDataExtractor, JSONKey

@extractor_for('respect-shoes.ru')
class RespectExtractor(AbstractDataExtractor):
    # Examples:
    #    https://respect-shoes.ru/slipony_lakovye_sinie_vk74_096686
    #    https://respect-shoes.ru/tufli_otkrytye_s56_085204

    _TYPE_SELECTOR = 'ul.breadcrumbs li:nth-last-child(2) a'
    _GENDER_SELECTOR = 'ul.breadcrumbs > li:nth-child(2) a'
    _NAME_SELECTOR = 'div.product-page__information h1'
    _PRICE_SELECTOR = 'div.product__cost b'
    _SIZES_SELECTOR = 'div.size-selector a'

    _ATTRIBUTE_NAMES_SELECTOR = 'div#description-tooltip-content dt'
    _ATTRIBUTE_VALUES_SELECTOR = 'div#description-tooltip-content dd'

    def _parse_brand(self):
        self._save_raw(JSONKey.BRAND_KEY, 'Respect')