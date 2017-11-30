from extract.abstract import extractor_for, AbstractDataExtractor, JSONKey

@extractor_for('www.ecco-shoes.ru')
class EccoExtractor(AbstractDataExtractor):
    # Examples:
    #    https://www.ecco-shoes.ru/catalog/621174/01001/
    #    https://www.ecco-shoes.ru/catalog/218033/01070/

    _TYPE_SELECTOR = 'ul.i-breadcrumb-way > li:nth-last-child(2) span'
    _GENDER_SELECTOR = 'ul.i-breadcrumb-way > li:nth-child(2) span'
    _NAME_SELECTOR = 'h1.header'
    _COLORS_SELECTOR = 'div.color > span'
    _SIZES_SELECTOR = 'div.size-range > span'
    _PRICE_SELECTOR = 'div.price-now > span'
    _IMG_SELECTOR = 'img.preview-image'

    _REVIEWS_SELECTOR = 'div.product-review-opinion div.description'
    _DESCRIPTION_SELECTOR = 'div.product-info > div.product-description > p.product-description-text'
    _ATTRIBUTE_NAMES_SELECTOR = 'div.product-info > ul.product-characteristic > li span.item-name'
    _ATTRIBUTE_VALUES_SELECTOR = 'div.product-info > ul.product-characteristic > li span.item-value'

    def _parse_brand(self):
        self._save_raw(JSONKey.BRAND_KEY, 'ECCO')
