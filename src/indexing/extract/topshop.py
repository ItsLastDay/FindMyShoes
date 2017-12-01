from typing import Optional

from extract.abstract import extractor_for, AbstractDataExtractor, JSONKey


@extractor_for('www.top-shop.ru')
class TopshopExtractor(AbstractDataExtractor):
    # Examples
    #   http://www.top-shop.ru/product/1788004-walkmaxx-comfort-2-0/
    #   http://www.top-shop.ru/product/1936663-trend-myagkost-cvet-seryy/


    _NAME_SELECTOR = 'h1.gr_zag_lev_1'
    _BRAND_SELECTOR = 'div.ic_brandname > a'
    _PRICE_SELECTOR = 'div[class="ic_main_price sale_price"]'
    _SIZES_SELECTOR = None # got only with modal dialog((
    _IMG_SELECTOR = 'div.ic_pic > a > img'

    _DESCRIPTION_SELECTOR = 'div#description'
    _REVIEWS_SELECTOR = 'div[class="row review_text"] div.user_text'
    _ATTRIBUTES_SELECTOR = 'div#characteristics > ul:nth-last-child(1)'

    COLOR_TEMPLATE = '. Цвет: '

    def _parse_name(self):
        data = self._selectable_data.cssselect(self._NAME_SELECTOR)
        if len(data) == 0:
            return
        name = data[0].text
        color_pos = name.find(self.COLOR_TEMPLATE)
        if color_pos != -1:
            name = name[:color_pos]
        self._save_raw(JSONKey.NAME_KEY, name)

    def _parse_price(self):
        def get_price_from_div():
            return ""
        data = self._selectable_data.cssselect('div.ic_main_price')
        if len(data) == 0:
            data = self._selectable_data.cssselect('div[class="ic_main_price sale_price"]')
        if len(data) == 0:
            return
        div = data[0]
        ch = div.getchildren()
        if len(ch) == 0:
            return
        price_str = ch[0].tail
        self._save_raw(JSONKey.PRICE_KEY, AbstractDataExtractor.price_from_string([price_str]))

    def _process_text(self, text: str):
        if text is None:
            return None
        text = text.replace('\n', ' ')
        text = text.replace('\t', ' ')
        text = text.replace('  ', ' ')
        text = text.replace('  ', ' ')
        return text.strip()

    def _parse_description(self):
        panels = self._selectable_data.cssselect(self._DESCRIPTION_SELECTOR)
        if len(panels) == 0:
            return
        panel = panels[0]
        text = ""
        for ch in panel.getchildren():
            if ch.text is not None:
                text += ch.text
            for ch1 in ch.getchildren():
                if ch1.text is not None:
                    text += ch1.text
                if ch1.tail is not None:
                    text += ch1.tail
        if len(text) > 0:
            self._save_raw(JSONKey.DESCRIPTION_KEY, self._process_text(text))

    def _parse_attributes(self):
        attributes = dict()
        uls = self._selectable_data.cssselect(self._ATTRIBUTES_SELECTOR)
        if len(uls) == 0:
            return
        for li in uls[0].getchildren():
            div = li.find('div')
            name = div.text
            values = list(map(lambda span: span.text, div.findall('span')))
            if len(values) == 0 or name is None:
                continue
            name = name.strip()[:-1] # ':'
            if name == 'Цвет':
                self._save_raw(JSONKey.COLORS_KEY, values)
            elif name == 'Пол':
                self._save_raw(JSONKey.GENDER_KEY, self.unify_gender(' '.join(values)))
            else:
                attributes[name] = ' '.join(values)

        self._save_raw(JSONKey.ATTRIBUTES_KEY, attributes)
