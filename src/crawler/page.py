# Andrey
import re
from datetime import datetime
from logging import getLogger
from typing import Optional
from urllib import parse

from bs4 import BeautifulSoup, Tag

from url_getter import URLGetter

page_logger = getLogger("page")


class PageException(BaseException):
    pass


QUELLE_LINK_PREFIX = '//www.quelle.ru'


class Page:
    def __init__(self, domain_url: str, path: str = '/'):
        """
        Page is created by text URL.
        `self.url` should point to this URL.
        :param domain_url: like https://www.lamoda.ru (may be reference to some path, but only with path equal to '/').
        :param path: Path inside domain, should start with '/'
        """
        # < scheme >: // < netloc > / < path >? < query >  # <fragment>
        if not path.startswith('/'):
            raise PageException("page path should start with '/'")

        if not domain_url.startswith("http"):
            raise PageException("domain_url should start with http[s]:// protocol")

        scheme, netloc, domain_path, query = parse.urlsplit(domain_url)[:4]
        if query:
            domain_path += '?' + query
        # just in case.
        if netloc.endswith('/'):
            netloc = netloc[:-1]
        if len(domain_path) > 0 and domain_path != "/":
            assert path == '/'
            path = domain_path
        if query != '':
            # 200: https://www.lamoda.ru/c/15/shoes-women/?sitelink=topmenuW&l=3&page=1
            # 400: https://www.lamoda.ru/c/15/shoes-women/?sitelink=topmenuW&l=3&page=1/
            path = path.rstrip('/')

        # quelle bad links like '//www.quelle.ru/home/all-action-codes/'
        if path.startswith(QUELLE_LINK_PREFIX):
            path = path[len(QUELLE_LINK_PREFIX):]

        self._domain_url = "{}://{}".format(scheme, netloc)
        assert path.startswith('/') and (len(path) == 1 or path[1] != '/')

        # just in case.
        while len(path) > 1 and path[-2:] == '//':
            path = path[:-1]
        self._path = path
        self._mtime = None
        self._text = None
        self._soup = None

    # Getters #
    def url(self):
        assert self._path.startswith('/')
        return self._domain_url + self._path

    def path(self):
        return self._path

    def domain_url(self):
        return self._domain_url

    def can_be_stored(self) -> Optional[bool]:
        """Checks that we are allowed to store this page.

        Checks for <META NAME="..."> tags. "noindex" keyword
        means that we should not store the page.

        Returns: boolean.
        """
        if self._soup is None:
            return None
        from storage import PageFilter
        if self._meta_tags_content_has_property("noindex"):
            page_logger.debug('Page "{}" cannot be stored because of noindex property'.format(self.url()))
            return False

        if not PageFilter.should_be_stored(self):
            page_logger.debug('Page "{}" cannot be stored because of PageFilter settings'.format(self.url()))
            return False
        page_logger.debug('OK, Page "{}" can be stored'.format(self.url()))
        return True

    def fetch(self):
        """Query self.url, Download HTTP response of the server.

        Our crawler is polite, so it identifies itself as "findmyshoes_robot"
        Populates the result in this object (i.e. page content, children, etc.).

        If response status is not 200-OK, then subsequent calls to `can_be_stored` 
        and `can_be_crawled` should return empty values.

        Returns: nothing.
        """
        page_logger.debug('Fetching page {}'.format(self.url()))
        response = URLGetter.get_response(self.url())
        if response.status_code != 200:
            page_logger.info("Failed to fetch page {} with status code {}".format(self.url(), response.status_code))
            assert not response.ok
        else:
            self._soup = BeautifulSoup(response.text, "lxml")

    def children(self) -> ['Page']:
        """Returns all pages that current page points to.

        Should return empty list if <META NAME="..."> contains "nofollow".

        Returns: 
            list of `Page` objects.
        """
        if self._soup is None or self._meta_tags_content_has_property("nofollow"):
            return []

        def get_path_from_link(link: Tag):
            path = link.get('href')
            if path is None:
                path = link.get('data-link')

                # If found an internal link and it doesn't lead to external site.
                if path is not None and path.startswith('/'):
                    path = "{}{}".format(self._domain_url, path)

            # href attribute is not present or leads to external domain.
            if path is None or (path.startswith('http') and not path.startswith(self._domain_url)):
                return None

            if path.startswith(self._domain_url):
                path = path[len(self._domain_url):]

            if not path.startswith('http') and not path.startswith('/'):
                path = '/' + path
            return path


        def path_filter(path):
            return path is not None and \
                path.startswith('/') and \
                   (path[:2] != "//" or
                    path[:len(QUELLE_LINK_PREFIX)] == QUELLE_LINK_PREFIX)

        valid_paths = list(filter(path_filter, map(get_path_from_link, self._soup.find_all('a'))))

        # Dirty hack for lamoda: start from pages of the form
        # https://www.lamoda.ru/c/15/shoes-women/?sitelink=topmenuW&l=3&page=XXX
        # and go only to product pages.
        if 'lamoda' in self._domain_url:
            # For every boots, there are pages for each size, like
            # https://www.lamoda.ru/p/lo019awxqe31/shoes-lostink-valenki/?sku=LO019AWXQE31E370
            # They are not 100% identical, but in essense, they are.
            valid_paths = list(filter(lambda path: path.startswith('/p/')
                and '?sku=' not in path, valid_paths))

        def path_does_not_contains(path: str, substrings: [str]):
            return all(map(lambda ss: path.find(ss) == -1, substrings))

        def filter_children_paths(valid_paths, substrings: [str]):
            return list(filter(lambda path: path_does_not_contains(path, substrings), valid_paths))


        if 'my-shop' in self._domain_url:
            valid_paths = filter_children_paths(valid_paths, ['forum', 'help', 'books', 'toys', 'javascript', 'cgi-bin'])
            # shoes accessories are commented out.
            my_shop_catalogue_numbers = [
                19401,
                19446,
                # 19448,
                # 19449,
                # 19450,
                # 19451,
                19503,
                19504,
                19505,
                19506,
                19508,
                19509,
                19510,
                14049,
                14051,
                14052,
                14053,
                15001,
                # 15003,
                15474,
                15478,
                15628,
                15629,
                15630,
                15631,
                20120,
                20122,
                20124
            ]
            def my_shop_catalogue_filter(path):
                if path.find('/shop/catalogue/') == -1:
                    return True
                else:
                    return any(map(lambda number: str(number) in path, my_shop_catalogue_numbers))
            valid_paths = list(filter(my_shop_catalogue_filter, valid_paths))

        if 'shop24' in self._domain_url:
            valid_paths = filter_children_paths(valid_paths, ['content',
                                                              'basket',
                                                              'odezhda',
                                                              'bluzki',
                                                              'bryuki'
                                                              'dzhinsy',
                                                              'zhakety',
                                                              'kostyumy',
                                                              'kupalniki',
                                                              'pulovery',
                                                              'futbolki',
                                                              'shorty',
                                                              'yubki',
                                                              'sumki',
                                                              'zonty',
                                                              'komplekty',
                                                              'koshelki',
                                                              'ochki',
                                                              "perchatki",
                                                              "remni",
                                                              "ukrasheniya",
                                                              "sharfy-platki",
                                                              "chasy",
                                                              "baletki",
                                                              "rubashki",
                                                              "galstuki",
                                                              "golovnye-ubory",
                                                              "platya",
                                                              "raznoe",
                                                              "igrushki",
                                                              "kollekcii",
                                                              "dekorativnaya-kosmetika",
                                                              "parfyumeriya",
                                                              "sredstva",
                                                              "pribory",
                                                              "tovary-dlya-zdorovya",
                                                              "sportivnoe-pitanie-bad",
                                                              "tovary-dlya-plavaniya",
                                                              "fitnes-aktivnyj-otdyh",
                                                              "professionalnaya-kosmetika",
                                                              "dlya-doma",
                                                              "vannaya",
                                                              "aksessuary",
                                                              "zanaveski-dlya-dusha",
                                                              "kovriki",
                                                              "polotenca",
                                                              "hranenie-v-vannoj",
                                                              "dekor",
                                                              "kovry",
                                                              "shtory",
                                                              "osvecshenie",
                                                              "rukodelie",
                                                              "kuhnya-stolovaya",
                                                              "stolovaya-posuda",
                                                              "kuhon",
                                                              "hranenie-produktov",
                                                              "produkty",
                                                              "spalnya",
                                                              "dekorativnye-podushki-pokryvala",
                                                              "detskoe-postelnoe-bele",
                                                              "posteln",
                                                              "detskaya",
                                                              "odeyala-podushki",
                                                              "pokryvala-pledy",
                                                              "postelnoe-bele",
                                                              "hoztovary-tovary-dlya-dachi",
                                                              "tovary-dlya-uborki-i-hraneniya",
                                                              "hozyajstvennye-tovary-instrumenty",
                                                              "bytovaya-himiya",
                                                              "tovary-dlya-sada-i-dachi",
                                                              "tehnika-dlya-doma",
                                                              "tovary-dlya-sauny-i-bani",
                                                              "tovary-dlya-zhivotnyh",
                                                              ]
                                                )

        if 'quelle' in self._domain_url:
            valid_paths = filter_children_paths(valid_paths, [
                'basket', 'wishlist', 'register',
                'accesories', 'accessoires', 'kitchen', 'cleaning',
                'decor', 'skirts', 'sweaters', 'blazers', 'furniture', 'wear', 'cloth', 'dress',
                'carpets', 'towels', 'shirts', 'jacket',
                'trousers', 'pullovers', 'coats', 'curtains',
                'blouses', 'coats', 'jeans', 'shorts', 'suits',
                'textiles', 'decoration', 'bathroom', 'animals',
                'kardigans',
                'services', 'content'
            ]
                                                )


        # query 'site:kinderly.ru' returned 50k pages - should be crawlable in a day.
        if 'kinderly' in self._domain_url:
            pass

        if 'top-shop' in self._domain_url:
            valid_paths = filter_children_paths(valid_paths, [
                'bytovaya-tehnika',
                'tovary-dlya-doma',
                'stroitelstvo-i-remont',
                'dacha-sad-i-ogorod',
                'elektronika',
                'tovary-dlya-avtomobilya'
                , 'krasota-i-zdorove'
                , 'tovary-dlya-detey'
                , 'podarki-vse-dlya-prazdnika'
                , 'dostavka-i-oplata'
                , 'hotline'
                , 'contacts'
                , 'bytovaya-tehnika'
                , 'tovary-dlya-doma'
                , 'stroitelstvo-i-remont'
                , 'tovary-dlya-sporta'
                , 'dacha-sad-i-ogorod'
                , 'elektronika'
                , 'tovary-dlya-avtomobilya'
                , 'krasota-i-zdorove'
                , 'tovary-dlya-detey'
                , 'turizm-i-otdyh'
                , 'hobbi-i-razvlecheniya'
                , 'kanctovary'
                , 'zoo-tovary'
                , 'knigi'
            ])

        if 'wildberries' in self._domain_url:
            valid_paths = filter_children_paths(valid_paths, [
                'services',
                'aksessuary',
                'knigi',
                'dom-i-dacha',
                'sport',
                'igrushki',
                'krasota',
                'novinki',
                'elektronika',
                'yuvelirnye-ukrasheniya',
                'premium',
                'podarki',
                'novyy-god',
                'odezhda',
                'belya',
                'kupalniki',
                'bolshie-razmery',
                'trusy',
                'byustgaltery',
                'plyazhnaya-moda',
                'kolgotki-i-chulki',
                'mayki',
                'erotik',
                'korrektiruyushchee-bele',
                'kombidressy',
                'bandazhi',
                'bodi-i-korsety',
                'kombinatsii-i-neglizhe',
                'komplekty-belya',
                'termobele',
                'poyasa-dlya-chulok',
                'podvyazki',
                'nizhnie-yubki',
                'dzhinsy-bryuki',
                'zhilety',
                'kostyumy',
                'pidzhaki-zhakety',
                'platya',
                'pulovery-kofty-svitery',
                'yubki',
                'bele',
                'bluzki-koftochki',
                'bryuki-dzhinsy',
                'tuniki',
                'kostyumy-kombinezony',
                'pidzhaki-zhilety',
                'platya-sarafany',
                'pulovery-dzhempery',
                'futbolki',
                '/look/'
            ])
            # Surpassing rule '*?*' in robots.txt
            valid_paths = list(map(lambda path: path if path.find('?') == -1 else path[:path.find('?')], valid_paths))

        if 'onlinetrade' in self._domain_url:
            valid_paths = filter_children_paths(valid_paths, [
                'basket',
                'news'
                'telefony',
                'tekhnika'
                'foto_video',
                'kompyutery_i_periferiya',
                'planshety_i_noutbuki',
                'tv_i_video',
                'avto_i_mototovary',
                'bezopasnost_i_videonablyudenie',
                'krasota_i_zdorove',
                'parfyumeriya_i_kosmetika',
                'apteka',
                'stroitelstvo_i_remont',
                'osveshchenie',
                'tovary_dlya_doma',
                'sad_i_ogorod',
                'mebel',
                'detskie_tovary',
                'detskie_igrushki',
                'muzykalnoe_oborudovanie',
                'igry_i_pristavki',
                'sport_otdykh_turizm',
                'khobbi_i_tvorchestvo',
                'zootovary',
                'chasy_i_podarki',
                'knigi',
                'produkty_pitaniya',
                'karnavalnye_kostyumy',
                'karnavalnye_kostyumy',
                'mikrofony',
                'noutbuki',
                'sertifikat'','
                'blendery',
                'zimnie_shiny',
                'zootovari',
                'produkty_pitaniya',
                'knigi',
                'maslyanye_obogrevateli',
                'osveshchenie',
                'tovary_dlya_turizma_i_otdykha',
                'bytovaya_khimiya',
                'sportivnoe_pitanie',
                'detskie_tovary',
                'tekstil',
                'apteka',
                'elektroinstrumenty',
                'bagazhniki_boksy_krepleniya',
                'sport_otdykh_turizm',
                'avtomobil',
                'snegouborshchiki',
                'prezervativy',
                'blendery',
                'rascheski'
                'protsessory',
                'kompyuternye_korpusa',
                'avtomobilnye_videoregistratory',
                'vitaminy',
                'shvabry',
                'mediapleery',
                'spalnye_meshki',
                'ochistiteli',
                'vyazanie',
                'kamery'
                'ssd_diski'
                'tetradi'
                'sredstva_dlya_posudomoechnykh_mashin',
                'tsifrovye_zerkalnye_fotoapparaty',
                'kapelnye_kofevarki_i_kofevarki_turki',
                'igrushek',
                'protsessory',
                'rascheski',
                'kamery',
                'news',
                'info',
                '/shops/'
            ]
                                                )

        if 'kctati' in self._domain_url:
            valid_paths = filter(lambda path: path.find('?') == -1 or ('?PAGEN' in path), valid_paths)

        if 'ozon' in self._domain_url:
            # valid_paths = filter(lambda path: path.find('?') == -1 or ('?PAGEN' in path), valid_paths)
            valid_paths = filter_children_paths(valid_paths, set([
                'clothing',
                'wedding',
                'apparel',
                'accessories',
                'jewelry',
                'tea',
                'coffee',
                'drink',
                'sweet-stuff',
                'pasta',
                'condiments-spices',
                'oil-sauces',
                'nuts-berries',
                'syrups-toppings',
                'cereals',
                'salt-sugar',
                'snacks',
                'corn-flakes',
                'dough',
                'meat-fish',
                'vegetables-fruits',
                'cheese',
                'sausages',
                'mushrooms-algae',
                'food',
                'flour',
                'tea-accessories',
                'pickles',
                'eggs',
                'farmers',
                'stationery',
                'paper',
                'demonstration',
                'office-supplies',
                'brief-bag',
                'pcgame',
                'console',
                'soft',
                'movie',
                'kino',
                'video',
                'detfilm',
                'dvdmusic',
                'jazz',
                'pop',
                'theremin',
                'rock',
                'classic',
                'wom',
                'vinyl',
                'actionantiques',
                'rar',
                'prints-cards',
                'collecting',
                'interior-decorations',
                'faberge',
                'author-work',
                'limoges',
                'div_luxury_gifts',
                'aged',
                'ebook',
                'eabook',
                'digital_journal',
                'game',
                'soft_home',
                'login',
                'orderlist',
                'favourites',
                'cart',
                'div_fashion',
                'clothing',
                'business'
                'div_overhaul',
                'div_kid',
                'div_hobby',
                'div_beauty',
                'div_pharmacy',
                'div_bs',
                'div_fashion',
                'div_food',
                'div_animals',
                'cargoods',
                'div_writing',
                'div_soft',
                'div_dvd',
                'div_music',
                'div_rar',
                'div_egoods',
                'certificat',
                'div_travel',
                'discount-goods',
                'div_adult',
                'nonfiction',
                'edlitera',
                'family',
                'book',
                'business',
                'foreign',
                'outofprint',
                'modern',
                'audiobook',
                'bookaction',
                'mobile',
                'laptop',
                'comp',
                'photo',
                'digital',
                'tech-audio',
                'tech_accessory',
                'gamebox',
                'ebooks',
                'largeapp',
                'app_refrigerators',
                'app_kitchen',
                'app_household',
                'app_beauty',
                'household-consumables',
                'kitchen',
                'textile',
                'interior',
                'chemical',
                'sauna',
                'garden',
                'illumination',
                'sanengineering',
                'holiday-decorations',
                'goods-storage',
                'carpets',
                'homerepair',
                'app_powertools',
                'bathroom-fittings',
                'wall-decoration',
                'measuring-tools',
                'electrotechnical-equipment',
                'adhesives-sealants',
                'heating',
                'paints-varnishes',
                'conditioning-ventilation',
                'fixture-hardware',
                'tools-storage',
                'doors',
                'repair-accessories',
                'coatings-insulation',
                'building-mixtures',
                'bathhouse-sauna',
                'toy',
                'toys',
                'education',
                'childrens-party',
                'newborns',
                'kids-cosmetics',
                'mums',
                'board-games',
                'hobby',
                'handiwork',
                'paper-crafts',
                'collectibles',
                'drawing-modeling',
                'cosmotheca',
                'perfum',
                'decorcosmetics',
                'haircare',
                'organic',
                'facecare',
                'hygiene',
                'sets',
                'glasses',
                'hcosm',
                'divadult',
                'men-cosmetics',
                'sport',
                'travel',
                'tourism',
                'bs_fishing',
                'sportnutrition',
                'fitness-equipment',
                'actions?pcat=cloth ',
                'final_sale',
                'detailid/34091447/',
                'clothing_men',
                'pasta',
                'condiments-spices',
                'baby-food',
                'oil-sauces',
                'canned-food',
                'nuts-berries',
                'syrups-toppings',
                'cereals',
                'salt-sugar',
                'snacks',
                'corn-flakes',
                'dough',
                'meat-fish',
                'vegetables-fruits',
                'cheese',
                'sausages',
                'mushrooms-algae',
                'milk-food',
                'fast-food',
                'flour',
                'tea-accessories',
                'pickles',
                'eggs',
                'farmers',
                'stationery',
                'paper',
                'demonstration-equipment',
                'drawing-accessories',
                'office-supplies',
                'brief-bag',
                'school',
                'pcgame',
                'console',
                'soft',
                'edusoft',
                'movie',
                'kino',
                'video',
                'detfilm',
                'dvdmusic',
                'jazz',
                'pop',
                'theremin',
                'rock',
                'classic',
                'wom',
                'vinyl',
                'actionantiques',
                'rar',
                'prints-cards',
                'collecting',
                'interior-decorations',
                'faberge',
                'author-work',
                'limoges'
            ])
                                                )

        return list(map(lambda path: Page(self._domain_url, path), valid_paths))

    def get_cleaned_response(self) -> str:
        """Retrieve page's html content.
        :return: html content of page.
        """
        return str(self._soup)

    def mtime(self) -> datetime:
        """Returns the time the page was last fetched.
        This is useful for long-running web spiders that need to check for new robots.txt files periodically."""
        return self._mtime

    def modified(self) -> None:
        """Sets the time this page was last fetched to the current time."""
        self._mtime = datetime.now().time()

    def _meta_tags_content_has_property(self, property_name: str) -> bool:
        robots_metas = self._soup.findAll('meta', attrs={'name': re.compile(r'^robots', re.I)})

        def tag_content_has_property(tag):
            for key in ['CONTENT', 'content']:
                if tag.get(key, '').lower().find(property_name.lower()) != -1:
                    return True
            return False

        return any(map(tag_content_has_property, robots_metas))
