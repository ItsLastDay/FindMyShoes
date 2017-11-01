import lxml
import lxml.html.clean

domain_extractors = dict()

def get_extractor_for_domain(domain):
    # Create new object every time, so we can save some state.
    return domain_extractors[domain]()

def extractor_for(domain):
    def f(cls):
        domain_extractors[domain] = cls

    return f


def _get_single_value(selector_result):
    if not selector_result:
        return None
    return selector_result[0]

def _get_list_of_values(selector_result):
    return selector_result


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
    _ATTRIBUTE_NAMES_SELECTOR = None
    _ATTRIBUTE_VALUES_SELECTOR = None

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
            "javascript": True,         # strip javascript
            "page_structure": False,    # leave page structure alone
            "style": True               # remove CSS styling
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

        # Unstructured info
        self._parse_description()
        self._parse_reviews()
        self._parse_attributes()

    def _get_data_by_selector(self, selector):
        texts = map(lambda x: x.text, self._selectable_data.cssselect(selector))
        not_none = filter(lambda x: bool(x), texts)
        return list(map(lambda x: x.strip(), not_none))

    def _get_raw_data_by_selector(self, selector):
        return self._selectable_data.cssselect(selector)

    def _save(self, key_name, selector, 
            postprocess_func=_get_single_value):
        if selector is None:
            return

        data = self._get_data_by_selector(selector)
        data = postprocess_func(data)
        if data:
            self._result_dict_ref[key_name] = data

    def _save_raw(self, key_name, value):
        if value:
            self._result_dict_ref[key_name] = value


    # I guess the following methods could be replaced by some clever
    # reflection, but current approach is more straightforwardly extensible.

    def _parse_name(self):
        self._save('name', self._NAME_SELECTOR)
    def _parse_brand(self):
        self._save('brand', self._BRAND_SELECTOR)
    def _parse_type(self):
        self._save('type', self._TYPE_SELECTOR)
    def _parse_colors(self):
        self._save('colors', self._COLORS_SELECTOR, _get_list_of_values)
    def _parse_price(self):
        self._save('price', self._PRICE_SELECTOR)
    def _parse_sizes(self):
        self._save('sizes', self._SIZES_SELECTOR, _get_list_of_values)
    def _parse_gender(self):
        self._save('gender', self._GENDER_SELECTOR)

    def _parse_description(self):
        self._save('description', self._DESCRIPTION_SELECTOR)
    def _parse_reviews(self):
        self._save('reviews', self._REVIEWS_SELECTOR, _get_list_of_values)
    def _parse_attributes(self):
        if self._ATTRIBUTE_NAMES_SELECTOR is None or self._ATTRIBUTE_VALUES_SELECTOR is None:
            return

        attributes = dict()
        for name, val in zip(self._get_data_by_selector(self._ATTRIBUTE_NAMES_SELECTOR),
                self._get_data_by_selector(self._ATTRIBUTE_VALUES_SELECTOR)):
            attributes[name] = val

        self._save_raw('attributes', attributes)


@extractor_for('www.bonprix.ru')
class BonprixExtractor(AbstractDataExtractor):
    # Examples: 
    #    https://www.bonprix.ru/produkty/pantolety-iz-naturalnoj-kozhi-bezhevyj-919945/#image,  
    #    https://www.bonprix.ru/produkty/kedy-bez-shnurkov-sinijbelyj-v-kletku-929840/#image 

    _NAME_SELECTOR = 'div h1.product-name'
    _GENDER_SELECTOR = 'div#breadcrumb span:nth-child(3) span'
    _PRICE_SELECTOR = 'span.price-tag > span.integer-place'
    _COLORS_SELECTOR = 'span.product-information > span.product-display-name'
    _SIZES_SELECTOR = 'ul#product-variant-size a'

    _DESCRIPTION_SELECTOR_1 = 'p.product-information-full-description'
    _DESCRIPTION_SELECTOR_2 = 'section#product-info h2'
    _ATTRIBUTE_NAMES_SELECTOR = 'strong.product-attribute-name'
    _ATTRIBUTE_VALUES_SELECTOR = 'span.product-attribute-value'
    _REVIEWS_SELECTOR = 'p.reviewText'

    def _parse_description(self):
        desc1 = self._get_data_by_selector(self._DESCRIPTION_SELECTOR_1)
        desc2 = self._get_data_by_selector(self._DESCRIPTION_SELECTOR_2)
        self._save_raw('description', '{}\n{}'.format(desc1, desc2))

    def _parse_sizes(self):
        data = self._get_raw_data_by_selector(self._SIZES_SELECTOR)
        # Example of .text_content(): "'\nНемецкий размер36\n\t"
        sizes = list(map(lambda x: x.text_content().strip()[-2:], data))
        if sizes:
            self._save_raw('sizes', sizes)


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
        self._save_raw('brand', 'Respect')


@extractor_for('ru.antoniobiaggi.com')
class AntonioExtractor(AbstractDataExtractor):
    # Examples:
    #    https://ru.antoniobiaggi.com/46699-tufli-muzhskie-kozhanye.html
    #    https://ru.antoniobiaggi.com/46761-tufli-zhenskie-kozhanye.html

    _NAME_SELECTOR = 'h1.name'
    _PRICE_SELECTOR = 'p.price'

    # The following two are intentionally same: site designers did a BAD job
    _COLORS_SELECTOR = 'li.colorBox span'
    _SIZES_SELECTOR = 'li.colorBox span'

    _ATTRIBUTES_SELECTOR = 'div.featuresXS > ul#boxscroll > li'

    def _parse_brand(self):
        self._save_raw('brand', 'Antonio Biaggi')

    def _parse_attributes(self):
        raw_attrs = self._get_data_by_selector(self._ATTRIBUTES_SELECTOR)
        attrs_dict = dict()

        for attr in raw_attrs:
            name, value = attr.split(':')
            attrs_dict[name] = value

        self._save_raw('attributes', attrs_dict)


@extractor_for('www.asos.com')
class AsosExtractor(AbstractDataExtractor):
    # Examples:
    #    http://www.asos.com/ru/asos/tufli-lodochki-s-bantikami-asos-pretty/prd/8629709?setPrefSite=true&r=1&mk=na
    #    http://www.asos.com/ru/love-moschino/lakirovannye-botinki-na-molnii-love-moschino/prd/8509013?clr=%D1%87%D0%B5%D1%80%D0%BD%D1%8B%D0%B9&cid=6992&pgesize=36&pge=0&totalstyles=605&gridsize=3&gridrow=1&gridcolumn=2

    _NAME_SELECTOR = 'div.product-hero > h1'
    _PRICE_SELECTOR = 'div#product-price span[data-id=current-price]'
    _COLORS_SELECTOR = 'div#product-colour span.product-colour'
    _SIZES_SELECTOR = 'div.layout-aside div.colour-size  [data-id=sizeSelect] option'
    _GENDER_SELECTOR = 'div#breadcrumb > ul > li:nth-child(2) > a'

    _DESCRIPTION_SELECTOR_1 = 'div#product-details div.product-description > span  > ul > li'
    _DESCRIPTION_SELECTOR_2 = 'div#product-details div.about-me span'

    def _parse_description(self):
        desc1 = self._get_data_by_selector(self._DESCRIPTION_SELECTOR_1)
        desc2 = self._get_data_by_selector(self._DESCRIPTION_SELECTOR_2)
        self._save_raw('description', '{}\n{}'.format(desc1, desc2))


@extractor_for('www.lamoda.ru')
class LamodaExtractor(AbstractDataExtractor):
    # Examples:
    #    https://www.lamoda.ru/p/lo019awgvm60/shoes-lostink-bosonozhki/
    #    https://www.lamoda.ru/p/oo001awkvi31/shoes-oodji-baletki/

    _BRAND_SELECTOR = 'a.ii-product__brand-text'
    _NAME_SELECTOR = 'h1.ii-product__title'
    _GENDER_SELECTOR = 'div.breadcrumbs span:nth-child(2) span'
    _TYPE_SELECTOR = 'div.breadcrumbs span:nth-last-child(1) span'
    _SIZES_SELECTOR = 'div.ii-select__columns > div.ii-select__column_native > div.ii-select__option'

    _ATTRIBUTE_NAMES_SELECTOR = 'div.ii-product__attributes > div > span.ii-product__attribute-label'
    _ATTRIBUTE_VALUES_SELECTOR = 'div.ii-product__attributes > div > span.ii-product__attribute-value'
    _DESCRIPTION_SELECTOR = 'div.ii-product__description-text > div[itemprop=description]'
    _REVIEWS_SELECTOR = 'div.rev__node_review > div.rev__node-body[itemprop=description]'


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

    _REVIEWS_SELECTOR = 'div.product-review-opinion div.description'
    _DESCRIPTION_SELECTOR = 'div.product-info > div.product-description > p.product-description-text'
    _ATTRIBUTE_NAMES_SELECTOR = 'div.product-info > ul.product-characteristic > li span.item-name'
    _ATTRIBUTE_VALUES_SELECTOR = 'div.product-info > ul.product-characteristic > li span.item-value'

    def _parse_brand(self):
        self._save_raw('brand', 'ECCO')
