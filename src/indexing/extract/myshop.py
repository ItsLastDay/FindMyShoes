from typing import Optional

from extract.abstract import extractor_for, AbstractDataExtractor, JSONKey

@extractor_for('my-shop.ru')
class MyshopExtractor(AbstractDataExtractor):
    _NAME_SELECTOR = 'div[class="pad4 product"] > h1' # h1[itemprop="name"] didn't work.
    _BRAND_SELECTOR = 'table[class="datavar v1"] > tr:nth-child(1) > td:nth-child(2) > a'
    _TYPE_SELECTOR = 'table[class="datavar v1"] > tr:nth-child(2) > td:nth-child(2) > a'
    _COLORS_SELECTOR = None  # TODO find in description.
    _PRICE_SELECTOR = 'td[class="bgcolor_2 list_border"] > b'
    _GENDER_SELECTOR = None # TODO find in description?
    _IMG_SELECTOR = 'img.fotorama_open'

    _DESCRIPTION_SELECTOR = 'div[itemprop="description"]'
    _REVIEWS_SELECTOR = 'div#tabs-6 > br'
    _ATTRIBUTES_TABLE_SELECTOR = 'table[class="bsp0 w100p"]'

    def _parse_name(self):
        namestr = self._selectable_data.cssselect(self._NAME_SELECTOR)[0].text

        # 'Тапочки с "памятью" "Комфорт", размер: 37-39'
        name = ','.join(namestr.split(',')[:-1])
        if len(name) == 0 and '(' in namestr:
            name = namestr[:namestr.find('(')].strip()
        if name is not None and len(name) > 0:
            self._save_raw(JSONKey.NAME_KEY, name)

    def _parse_sizes(self):
        # Стельки Salamander "Anti Odour" (с активированным углем), универсальные, размер 36-46
        # Мужская обувь сабо "Ионел", белые (размер: 45)
        # Тапочки с "памятью" "Комфорт", размер: 37-39
        name_str = self._selectable_data.cssselect(self._NAME_SELECTOR)[0].text
        try:
            for s in name_str.split(', '):
                if 'размер' in s:
                    size_str = ""
                    i = s.find('размер') + len('размер')
                    while i < len(s) and not s[i].isdigit():
                        i += 1
                    if s[i].isdigit():
                        while i < len(s) and (s[i].isdigit() or s[i] == '-'):
                            size_str += s[i]
                            i += 1
                    if '-' in size_str:
                        a, b = list(map(int, size_str.split('-')))
                        sizes = list(map(float, range(a, b + 1)))
                    else:
                        sizes = [float(size_str)]
                    self._save_raw(JSONKey.SIZES_KEY, sizes)
        except Exception:
            return

    def fix_value(self, value_str):
        if value_str is not None:
            return value_str.replace('\xa0', ' ').strip()

    def _parse_attributes(self):
        attributes = dict()
        tables = self._selectable_data.cssselect(self._ATTRIBUTES_TABLE_SELECTOR)
        if len(tables) > 0:
            try:
                # first one goes for full description.
                table = tables[-1]
                maintr = table.getchildren()[0]
                for td in maintr.getchildren():
                    inner_table = td.getchildren()[0]
                    for tr in inner_table.getchildren():
                        name_td, value_td = tr.getchildren()
                        name = name_td.find('span').text
                        value = value_td.text
                        a = value_td.find('a')
                        span = value_td.find('span')
                        if value is None and a is not None:
                            value = a.text
                        if value is None and span is not None:
                            value = span.text
                        value = self.fix_value(value)
                        name = self.fix_value(name)
                        if value is not None:
                            attributes[name] = value
            except Exception:
                # too complex logic - so many things can go wrong...
                return
        self._save_raw(JSONKey.ATTRIBUTES_KEY, attributes)

    def _parse_reviews(self):
        brs = self._selectable_data.cssselect(self._REVIEWS_SELECTOR)
        def process_review(text: str) -> Optional[str]:
            if text is None:
                return None
            while len(text) > 0 and text[0] == '\n':
                text = text[1:]
            while len(text) > 0 and text[-1] == '\n':
                text = text[:-1]
            while text[:2] == '• ':
                text = text[2:]
            return text if len(text) > 0 else None

        reviews = list(filter(lambda text: text is not None, map(lambda br: process_review(br.tail), brs)))
        if len(reviews) > 0:
            self._save_raw(JSONKey.REVIEWS_KEY, reviews)
