from extract.abstract import extractor_for, AbstractDataExtractor, JSONKey

@extractor_for('www.ozon.ru')
class OzonExtractor(AbstractDataExtractor):
    _NAME_SELECTOR = 'h1.bItemName'
    _BRAND_SELECTOR = 'div.eBrandLogo_logo > img'
    _TYPE_SELECTOR = None # in characteristics TODO extract from js.
    _COLORS_SELECTOR = 'span.eFabricColors_name'
    _PRICE_SELECTOR = 'span.eOzonPrice_main'
    _GENDER_SELECTOR = 'div[class^="bBreadCrumbs"] > div:nth-of-type(3) > a > span'
    _IMG_SELECTOR = 'img[class^="eMicroGallery_fullImage"]'

    _DESCRIPTION_SELECTOR = 'div.eItemDescription_text > p'
    _REVIEWS_SELECTOR = None # TODO extract from js
    _ATTRIBUTES_SELECTOR = None # TODO extract from js script from div.bBaseInfoColumn

    def _parse_name(self):
        data = self._selectable_data.cssselect(self._NAME_SELECTOR)
        if len(data) == 0 or data[0].text is None:
            return
        namestr = data[0].text.split(',')[:-1]
        self._save_raw(JSONKey.NAME_KEY, namestr)

    def _parse_brand(self):
        data = self._selectable_data.cssselect(self._BRAND_SELECTOR)
        if len(data) == 0:
            return
        img = data[0]
        if 'alt' in img.attrib:
            self._save_raw(JSONKey.BRAND_KEY, img.attrib.get('alt'))

    def _parse_colors(self):
        data = self._selectable_data.cssselect(self._COLORS_SELECTOR)
        if len(data) == 0:
            return
        colorstr = data[0].text
        if colorstr is None:
            return
        self._save_raw(JSONKey.COLORS_KEY, colorstr.split(', '))

    def _parse_sizes(self):
        data = self._selectable_data.cssselect(self._NAME_SELECTOR)
        if len(data) == 0 or data[0].text is None:
            return
        sizestr = data[0].text.split(', размер ')[-1]
        if not sizestr.isdigit():
            return
        self._save_raw(JSONKey.SIZES_KEY, self.process_sizes([sizestr]))
