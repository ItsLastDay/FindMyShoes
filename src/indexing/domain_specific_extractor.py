import lxml.etree

domain_extractors = dict()

def get_extractor_for_domain(domain):
    # Create new object every time, so we can save some state.
    return domain_extractors[domain]()

def extractor_for(domain)
    def f(cls):
        domain_extractors[domain] = cls

    return f


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

    _DESCRIPTION_SELECTOR = None
    _REVIEWS_SELECTOR = None
    _ATTRIBUTES_SELECTOR = None

    def __init__(self):
        self._selectable_data = None

    def parse_html(self, raw_html, result_dict):
        """ Populate `result_dict` with information.

        If we don't know how to extract certain piece of information,
        or when it is missing, do not populate the appropriate key.

        Returns: nothing.
        """
        self._selectable_data = lxml.etree.fromstring(raw_html)
        self._result_dict_ref = result_dict

        # Structured info
        self._parse_name()
        self._parse_brand()
        self._parse_type()
        self._parse_colors()
        self._parse_price()
        self._parse_sizes()
        self._parse_gender()

        # Unstructured info
        self._parse_description()
        self._parse_reviews()
        self._parse_attributes()

    def _get_data_by_selector(self, selector):
        return self._selectable_data.cssselect(selector)

    def _save(self, key_name, selector):
        self._result_dict_ref[key_name] = self._get_data_by_selector(selector)

    # I guess the following methods could be replaced by some clever
    # reflection, but current approach is more straightforwardly extensible.

    def _parse_name(self):
        self._save('name', _NAME_SELECTOR)
    def _parse_brand(self):
        self._save('brand', _BRAND_SELECTOR)
    def _parse_type(self):
        self._save('type', _TYPE_SELECTOR)
    def _parse_colors(self):
        self._save('colors', _COLORS_SELECTOR)
    def _parse_price(self):
        self._save('price', _PRICE_SELECTOR)
    def _parse_sizes(self):
        self._save('sizes', _SIZES_SELECTOR)
    def _parse_gender(self):
        self._save('gender', _GENDER_SELECTOR)

    def _parse_description(self):
        self._save('description', _DESCRIPTION_SELECTOR)
    def _parse_reviews(self):
        self._save('reviews', _REVIEWS_SELECTOR)
    def _parse_attributes(self):
        self._save('attributes', _ATTRIBUTES_SELECTOR)



@extractor_for('www.bonprix.ru')
class BonprixExtractor(AbstractDataExtractor):
    pass


@extractor_for('respect-shoes.ru')
class RespectExtractor(AbstractDataExtractor):
    pass


@extractor_for('ru.antoniobiaggi.com')
class AntonioExtractor(AbstractDataExtractor):
    pass


@extractor_for('www.asos.com')
class AsosExtractor(AbstractDataExtractor):
    pass


@extractor_for('www.lamoda.ru')
class LamodaExtractor(AbstractDataExtractor):
    pass


@extractor_for('www.ecco-shoes.ru')
class EccoExtractor(AbstractDataExtractor):
    pass
