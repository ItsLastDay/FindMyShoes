from typing import Optional

import lxml
import lxml.html.clean

class JSONKey:
    NAME_KEY = 'name'
    BRAND_KEY = 'brand'
    TYPE_KEY = 'type'
    COLORS_KEY = 'colors'
    SHOP_KEY = 'shop'
    PRICE_KEY = 'price'
    SIZES_KEY = 'sizes'
    IMG_KEY = 'image'

    GENDER_KEY = 'gender'
    GENDER_MEN = "M"
    GENDER_WOMEN = "Ж"
    GENDER_CHILDREN = "Д"

    DESCRIPTION_KEY = 'description'
    REVIEWS_KEY = 'reviews'
    ATTRIBUTES_KEY = 'attributes'


domain_extractors = dict()


def get_extractor_for_domain(domain):
    # Create new object every time, so we can save some state.
    try:
        return domain_extractors[domain]()
    except KeyError:
        # Can happen if there is no extractor.
        return None


def extractor_for(domain):
    def f(cls):
        domain_extractors[domain] = cls
        cls._shop = domain
    return f


# FIXME It's a dirty hack, neater site-specific fix required.
def _get_single_value(selector_result: [str]) -> Optional[str]:
    if not selector_result:
        return None
    # "&nbsp" seen on bonprix
    return selector_result[0].replace('&nbsp', '')


class AbstractDataExtractor:
    """Extract interesting data from html: type of shoes, brand, ... .

    Supported extracted info:
        Structured:
        name (as shown by e-shop, e.g. "Ботинки ECCO HOLTON 621174/01001")
        brand (e.g. "ECCO")
        type (e.g. "ботинки")
        colors - list of colors (e.g. ["белый", "чёрный"])
        price (in rubles, e.g. "11000")
        sizes - list of sizes in russian system (e.g. [39, 41, 42])
        gender - expected gender for shoe wearer, as shown by e-shop (e.g. "женская обувь" or "мужская")

        Unstructured:
        description - shoes description, as shown by e-shop
        reviews - list of user review texts
        attributes - dictionary of attributes that do not fall in "structured" category (or, at least, we don't know how to extract them). E.g. {'подкадка': 'мех', 'страна': 'Китай'}
    """
    _NAME_SELECTOR = None
    _BRAND_SELECTOR = None
    _TYPE_SELECTOR = None
    _COLORS_SELECTOR = None
    _PRICE_SELECTOR = None
    _SIZES_SELECTOR = None
    _GENDER_SELECTOR = None
    _IMG_SELECTOR = None

    _DESCRIPTION_SELECTOR = None
    _REVIEWS_SELECTOR = None
    _ATTRIBUTE_NAMES_SELECTOR = None
    _ATTRIBUTE_VALUES_SELECTOR = None

    _shop = "example.com"

    def __init__(self):
        self._selectable_data = None

    def parse_html(self, raw_html, result_dict):
        """ Populate `result_dict` with information.

        If we don't know how to extract certain piece of information,
        or when it is missing, do not populate the appropriate key.

        Returns: nothing.
        """
        # https://stackoverflow.com/a/22109680/5338270
        clean_args = {
            "javascript": True,  # strip javascript
            "page_structure": False,  # leave page structure alone
            "style": True  # remove CSS styling
        }
        clean_html = lxml.html.clean.Cleaner(**clean_args).clean_html(raw_html)

        self._selectable_data = lxml.html.fromstring(clean_html)
        self._result_dict_ref = result_dict

        # Structured info
        self._parse_name()
        self._parse_brand()
        self._parse_type()
        self._parse_colors()
        self._parse_price()
        self._parse_sizes()
        self._parse_gender()
        self._parse_image()
        self._save_raw(JSONKey.SHOP_KEY, self._shop)

        # Unstructured info
        self._parse_description()
        self._parse_reviews()
        self._parse_attributes()

    def _get_data_by_selector(self, selector: str) -> [str]:
        texts = map(lambda x: x.text, self._selectable_data.cssselect(selector))
        not_none = filter(lambda x: bool(x), texts)
        return list(map(lambda x: x.strip(), not_none))

    def _get_raw_data_by_selector(self, selector):
        return self._selectable_data.cssselect(selector)

    def _save(self, key_name, selector, postprocess_func=_get_single_value):
        """
        Stores value got by :param selector into dictionary by :param key.
        :param key_name:
        :param selector:
        :param postprocess_func:
        :return:
        """
        if selector is None:
            return

        data = self._get_data_by_selector(selector)
        data = postprocess_func(data)
        if data:
            self._result_dict_ref[key_name] = data

    def _save_array(self, key_name, selector):
        self._save(key_name, selector, lambda x: x)

    def _save_raw(self, key_name, value):
        # if value:
        self._result_dict_ref[key_name] = value

    # I guess the following methods could be replaced by some clever
    # reflection, but current approach is more straightforwardly extensible.

    def _parse_name(self):
        self._save(JSONKey.NAME_KEY, self._NAME_SELECTOR)

    def _parse_brand(self):
        self._save(JSONKey.BRAND_KEY, self._BRAND_SELECTOR)

    def _parse_type(self):
        self._save(JSONKey.TYPE_KEY, self._TYPE_SELECTOR)

    def _parse_colors(self):
        self._save_array(JSONKey.COLORS_KEY, self._COLORS_SELECTOR)

    def _parse_price(self):
        def price_from_string(prices_array: str) -> Optional[int]:
            if prices_array:
                s = prices_array[0]
                num_string = ''.join(c for c in s if c.isdigit())
                if num_string:
                    return int(num_string)
                else:
                    return s
            return None
        self._save(JSONKey.PRICE_KEY, self._PRICE_SELECTOR, price_from_string)

    def _parse_image(self):
        data = self._selectable_data.cssselect(self._IMG_SELECTOR)
        if not data:
            return
        x = data[0].get('src')
        if x.startswith('/'):
            x = self._shop + x
        if not x.startswith('http'):
            x = 'http://' + x
        self._result_dict_ref[JSONKey.IMG_KEY] = x

    def _parse_sizes(self):
        # TODO allow half sizes and check how they are specified at different shops.
        def process_sizes(sizes: [str]):
            if sizes:
                # There can be sizes like "35-43"
                if '-' in sizes[0]:
                    start, stop = sizes[0].split('-')
                    sizes = list(range(int(start), int(stop) + 1))
                return list(map(str, sizes))
            return None
        self._save(JSONKey.SIZES_KEY, self._SIZES_SELECTOR, process_sizes)

    def _parse_gender(self):
        def unify_gender(ss: [str]) -> str:
            # assert len(ss) == 1
            string_value = ss[0]
            si = string_value.lower()
            if 'жен' in si:
                return JSONKey.GENDER_WOMEN
            elif 'муж' in si:
                return JSONKey.GENDER_MEN
            elif 'дет' in si:
                return JSONKey.GENDER_CHILDREN
            return string_value

        self._save(JSONKey.GENDER_KEY, self._GENDER_SELECTOR, unify_gender)

    def _parse_description(self):
        self._save(JSONKey.DESCRIPTION_KEY, self._DESCRIPTION_SELECTOR)

    def _parse_reviews(self):
        self._save_array(JSONKey.REVIEWS_KEY, self._REVIEWS_SELECTOR)

    def _parse_attributes(self):
        if self._ATTRIBUTE_NAMES_SELECTOR is None or self._ATTRIBUTE_VALUES_SELECTOR is None:
            return

        attributes = dict()
        for name, val in zip(self._get_data_by_selector(self._ATTRIBUTE_NAMES_SELECTOR),
                             self._get_data_by_selector(self._ATTRIBUTE_VALUES_SELECTOR)):
            attributes[name] = val

        self._save_raw(JSONKey.ATTRIBUTES_KEY, attributes)
