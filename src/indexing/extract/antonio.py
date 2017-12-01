from extract.abstract import extractor_for, AbstractDataExtractor, JSONKey

@extractor_for('ru.antoniobiaggi.com')
class AntonioExtractor(AbstractDataExtractor):
    # Examples:
    #    https://ru.antoniobiaggi.com/46699-tufli-muzhskie-kozhanye.html
    #    https://ru.antoniobiaggi.com/46761-tufli-zhenskie-kozhanye.html

    _NAME_SELECTOR = 'h1.name'
    _PRICE_SELECTOR = 'p.price'

    # The following two are intentionally same: site designers did a BAD job
    # colors can be met with sizes in one list.
    _COLORS_SELECTOR = 'li.colorBox span'
    _SIZES_SELECTOR = 'li.colorBox span'

    _ATTRIBUTES_SELECTOR = 'div.featuresXS > ul#boxscroll > li'

    def _parse_brand(self):
        self._save_raw(JSONKey.BRAND_KEY, 'Antonio Biaggi')
        
    def _parse_colors(self):
        def filter_colors(colors: [str]):
            return list(filter(lambda s: s.isalpha(), colors))
        self._save(JSONKey.COLORS_KEY, self._COLORS_SELECTOR, filter_colors)

    def _parse_sizes(self):
        def filter_sizes(sizes: [str]):
            return list(map(float, filter(lambda s: s.isdigit(), sizes)))
        self._save(JSONKey.SIZES_KEY, self._SIZES_SELECTOR, filter_sizes)

    def _parse_attributes(self):
        raw_attrs = self._get_data_by_selector(self._ATTRIBUTES_SELECTOR)
        attrs_dict = dict()

        for attr in raw_attrs:
            name, value = attr.split(':')
            attrs_dict[name] = value.strip()
            
        self._save_raw(JSONKey.ATTRIBUTES_KEY, attrs_dict)
