from extract.abstract import extractor_for, AbstractDataExtractor, JSONKey

@extractor_for('www.wildberries.ru')
class WildberriesExtractor(AbstractDataExtractor):
    # Example
    #   https://www.wildberries.ru/catalog/1008827/detail.aspx

    _NAME_SELECTOR = 'div.good-header > h1'
    _TYPE_SELECTOR = 'div#add-options div.j-kit p.pp > span'
    _COLORS_SELECTOR = 'span[class="color j-color-name"]'
    _PRICE_SELECTOR = 'p[class="price j-price"] > ins'
    _SIZES_SELECTOR = 'label[class^="j-size"]'
    _GENDER_SELECTOR = None
    _IMG_SELECTOR = "img#preview-large"

    _DESCRIPTION_SELECTOR = 'div#description p'
    _REVIEWS_SELECTOR = 'div.comment-content p.body'
    _ATTRIBUTES_SELECTOR = 'div#add-options p.pp'

    def _parse_name(self):
        data = self._get_data_by_selector(self._NAME_SELECTOR)
        if len(data) > 0:
            self._save_raw(JSONKey.NAME_KEY, ', '.join(data[0].split(', ')[:-1]))

    def _parse_brand(self):
        data = self._get_data_by_selector(self._NAME_SELECTOR)
        if len(data) > 0:
            v = data[0].split(', ')[1]
            if len(v) > 1:
                self._save_raw(JSONKey.NAME_KEY, v[-1].strip())

    def _parse_sizes(self):
        # "35/5" "36/6" "41-42/6"
        def process_size(size):
            first = size.split('/')[0]
            if '-' in first:
                # dirty hack for wildberries - child shoes' sizes can be like '12-18мес'
                if 'мес' in first:
                    return []
                a, b = map(int, first.split('-'))
                return range(a, b + 1)
            else:
                first = first.replace(',', '.')
                if all(map(lambda c: c.isdigit() or c == '.', first)):
                    return [float(first)]
                else:
                    return []

        res_sizes = set()
        labels = self._selectable_data.cssselect(self._SIZES_SELECTOR)
        for label in labels:
            if 'disabled' in label.attrib['class']:
                continue
            span = label.find('span')
            if span is not None:
                res_sizes |= set(process_size(span.text))

        self._save_raw(JSONKey.SIZES_KEY, list(res_sizes))

    # def _parse_image(self):
    #     data = self._selectable_data.cssselect(self._IMG_SELECTOR)
    #     if len(data) == 0:
    #         return
    #     img = data[0]
    #     url = img.attrib['src']
    #     if url.startswith('//'):
    #         url = 'http:' + url
    #     self._save_raw(JSONKey.IMG_KEY, url)

    def _parse_attributes(self):
        attributes = dict()
        for attr in self._selectable_data.cssselect(self._ATTRIBUTES_SELECTOR):
            span = attr.find('span')
            if span is not None:
                name = attr.text[:-1]
                value = span.text.strip()
                if 'Пол' in name:
                    self._save_raw(JSONKey.GENDER_KEY, self.unify_gender(value))
                attributes[name] = value
        self._save_raw(JSONKey.ATTRIBUTES_KEY, attributes)
