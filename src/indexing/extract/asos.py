from extract.abstract import extractor_for, AbstractDataExtractor, JSONKey

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
    _TYPE_SELECTOR = 'div.product-description > span > a > strong'

    _DESCRIPTION_SELECTOR_1 = 'div#product-details div.product-description > span  > ul > li'
    _DESCRIPTION_SELECTOR_2 = 'div#product-details div.about-me span'

    def _parse_description(self):
        desc1 = self._get_data_by_selector(self._DESCRIPTION_SELECTOR_1)
        desc2 = self._get_data_by_selector(self._DESCRIPTION_SELECTOR_2)
        self._save_raw(JSONKey.DESCRIPTION_KEY, '{}\n{}'.format(desc1, desc2))

    def _parse_price(self):
        def process_price(prices: [str]):
            if prices:
                first_price = prices[0]
                return int(first_price[:first_price.index(',')])
            return None
        self._save(JSONKey.PRICE_KEY, self._PRICE_SELECTOR, process_price)