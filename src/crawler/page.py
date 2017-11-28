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
        if len(domain_path) > 0:
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
            valid_paths = filter_children_paths(valid_paths, ['forum', 'help', 'books', 'toys'])

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
                                                              "shkolnye",
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

        if 'kinderly' in self._domain_url:
            valid_paths = filter_children_paths(valid_paths, ['vodolazki', 'svitera', 'kofty', 'rantsy', 'kostyumy',
                                                              'kurtki',  'palto', 'odezhda', 'tolstovki', 'kardigany',
                                                              'shtany', 'kalsony', 'plavki', 'shorty', 'bridzhi',
                                                              'dzhinsy', 'kolgotki', 'kombinezony', 'polzunki',
                                                              'shtanishki', 'futbolochki', 'chepchiki', 'pelenki',
                                                              'termobelie', 'trikotazh', 'kraski', 'karandashy',
                                                              'kantstovary', 'fartuki', 'sportivnaia-forma', 'bryuki',
                                                              'trusy', 'shortiki',
                                                              'sumki', 'shkolnye', 'shkolnaia',
                                                              'platya',
                                                              'derevo',
                                                              'katalki',
                                                              'igrushki',
                                                              'kukly',
                                                              'page',
                                                              'nabor',
                                                              'konstruktor',
                                                              'ryukzaki',
                                                              'papki',
                                                              'penaly',
                                                              'albomy-dlya-risovaniya',
                                                              'bloknoty',
                                                              'karton',
                                                              'kisti',
                                                              'kley',
                                                              'markery',
                                                              'melki',
                                                              'nozhnitsy',
                                                              'plastilin-dlya-urokov-truda',
                                                              'ruchki',
                                                              'flomastery',
                                                              'tsvetnaya-bumaga',
                                                              'shtampy',
                                                              'brendy-rantsev-i-sumok',
                                                              'brauberg',
                                                              'de-lune',
                                                              'erichkrause',
                                                              'kite',
                                                              'brendy-rantsev-i-sumok',
                                                              'novinki-odezhdy',
                                                              'vetrovki',
                                                              'zhilety-uteplennye',
                                                              'po-tipu-odezhdy',
                                                              'bluzki',
                                                              'rubashki',
                                                              'longslivy',
                                                              'tuniki',
                                                              'dgemper-sviter',
                                                              'dzhemper',
                                                              'bolero',
                                                              'futbolki-maiki-topi',
                                                              'mayki',
                                                              'topy',
                                                              'detskie-futbolki',
                                                              'sarafany',
                                                              'komplekty-odezhdy',
                                                              'legginsy',
                                                              'yubki',
                                                              'kupalniki',
                                                              'noski',
                                                              'pizhamy',
                                                              'nizhnee-belie',
                                                              'nizhnie-mayki',
                                                              'komplekty-nizhnego-belya',
                                                              'halaty',
                                                              'golfy',
                                                              'getry',
                                                              'gamashi',
                                                              'bodi-dlya-novorozhdennyh',
                                                              'vyazannye-veschi',
                                                              'futbolki-koftochki',
                                                              'koftochki',
                                                              'raspashonki',
                                                              'komplekty-dlya-novorozhdennyh',
                                                              'pesochniki',
                                                              'nakolenniki',
                                                              'pinetki',
                                                              'tsarapki',
                                                              'shapochki',
                                                              'flisovye-poddevy',
                                                              'detskie-golovnye-ubory',
                                                              'varezhki',
                                                              'detskie-manishki',
                                                              'detskie-perchatki',
                                                              'detskie-shapki',
                                                              'shapki-slemy',
                                                              'sharfy',
                                                              'letnie-golovnye-ubory',
                                                              'detskie-kepki',
                                                              'detskie-panamy',
                                                              'aksessuary-dlya-odezhdy',
                                                              'galstuki',
                                                              'detskie-sumochki',
                                                              'detskie-chemodany',
                                                              'zontiki-detskie',
                                                              'remni-detskie',
                                                              'ukrasheniya-dlya-volos',
                                                              'banty',
                                                              'obodki',
                                                              'povyazki',
                                                              'rezinki',
                                                              'bazovyy-garderob',
                                                              'naryadnye-bluzki',
                                                              'naryudnye-ubki',
                                                              'naryadnie-aksessuary',
                                                              'brendy-odezhdy',
                                                              'shnurki',
                                                              'stelki',
                                                              'populyarnye-serii-igrushek',
                                                              'new-year',
                                                              'simvol-goda',
                                                              'novogodnie-podelki',
                                                              'novogodnie-ukrasheniya',
                                                              'prazdnik',
                                                              'kachalki',
                                                              'hodunki',
                                                              'busy',
                                                              'gorki',
                                                              'labirinty',
                                                              'ramki-vkladyshi',
                                                              'stuchalki',
                                                              'schety',
                                                              'shnurovki',
                                                              'dugi',
                                                              'podveski',
                                                              'nevalyashki',
                                                              'prorezyvateli',
                                                              'pogremushki',
                                                              'yuly',
                                                              'bizibordy',
                                                              'kubiki',
                                                              'piramidki',
                                                              'sortery',
                                                              'mobili',
                                                              'kovrik-pazl',
                                                              'razvivayuschie-kovriki',
                                                              'razvivayuschie-tsentry',
                                                              'razvivayuschie-knizhki',
                                                              'pazly-dlya-malyshey',
                                                              'nastolnye-igry',
                                                              'golovolomki',
                                                              'dorozhnye-igry',
                                                              'kartochnye-igry',
                                                              'logicheskie-igry',
                                                              'magnitnye-igri',
                                                              'na-lovkost',
                                                              'igry-hodilki',
                                                              'ekonomicheskie-igry',
                                                              'domino-i-loto',
                                                              'loto',
                                                              'mozaika',
                                                              'pazzly',
                                                              'fokusy',
                                                              'shahmaty-i-shashki',
                                                              'spinnery',
                                                              'kubik-antistress',
                                                              'derevyannye',
                                                              'magnitnye',
                                                              'elektronnye',
                                                              'plastmassovye',
                                                              'zheleznye',
                                                              'iz-kirpichikov',
                                                              'sbornye-modeli',
                                                              'geroi-i-serii',
                                                              'mattel-hot-wheels',
                                                              'lbx',
                                                              'my-little-pony',
                                                              'sylvanian',
                                                              'ben-i-holli',
                                                              'vspysh-i-chudo-mashinki',
                                                              'vroomiz',
                                                              'geroi-v-maskah',
                                                              'doktor-plyusheva',
                                                              'zvezdnye-voyny',
                                                              'mechi',
                                                              'figurki',
                                                              'masha-medved',
                                                              'minonygadkiy-ya',
                                                              'mstiteli',
                                                              'pozharnyy-sem',
                                                              'poli-robokar',
                                                              'princess-disney',
                                                              'super-wings',
                                                              'peppa-pig',
                                                              'tachki',
                                                              'tobot',
                                                              'transformers',
                                                              'trolli',
                                                              'fiksiki',
                                                              'holodnoe-serdtse',
                                                              'chuggington',
                                                              'chelovek-pauk',
                                                              'cherepashki-nindzya',
                                                              'shopkins',
                                                              'schenyachiy-patrul',
                                                              'esche-geroi-i-serii',
                                                              'palace-pets',
                                                              'ledi-bag-i-super-kot',
                                                              'sharlotta-zemlyanichka',
                                                              'yuhu-i-druzya',
                                                              'angry-birds',
                                                              'hello-kitty',
                                                              'little-charmers-2',
                                                              'littlest-pet-shop',
                                                              'power-rangers',
                                                              'regal-academy',
                                                              'betmen',
                                                              'v-poiskah-dori-nemo',
                                                              'vinni-puh',
                                                              'inside-out',
                                                              'zveropolis',
                                                              'kak-priruchit-drakona',
                                                              'katya-i-mim-mim',
                                                              'maylz-s-drugoy-planety-miles-from-tomorrowland',
                                                              'parovozik-tomas',
                                                              'samolety',
                                                              'printsessy-disneya',
                                                              'supergeroi',
                                                              'taynaya-zhizn-domashnih-zhivotnyh',
                                                              'filly',
                                                              'khoroshy-dinozavr',
                                                              'schenok-v-moem-karmane',
                                                              'glimmies',
                                                              'shimmer-and-shine',
                                                              'wissper',
                                                              'chubby-puppies',
                                                              'muzykalnye-instrumenty',
                                                              'baraban',
                                                              'buben',
                                                              'gitara',
                                                              'gubnaya-garmoshka',
                                                              'dudochka',
                                                              'ksilofon',
                                                              'marakasy-i-kastaniety',
                                                              'mikrofon',
                                                              'pianino',
                                                              'sintezator',
                                                              'pupsy',
                                                              'zamki',
                                                              'kolyaski',
                                                              'krovatki-dlya-kukol',
                                                              'mebel-i-aksessuary-dlya-kukol',
                                                              'transport-dly-kukol',
                                                              'lalaloopsy',
                                                              'shteffi',
                                                              'evi',
                                                              'equestria-girls',
                                                              'ever-after-high',
                                                              'monster-high',
                                                              'barbie',
                                                              'winx',
                                                              'nasledniki-disney',
                                                              'baby-annabell',
                                                              'baby-born',
                                                              'chou-chou',
                                                              'tovary-dlya-kukol',
                                                              'transport',
                                                              'avtotreki',
                                                              'garazhi-i-parkovki',
                                                              'dorozhnye-znaki',
                                                              'zheleznye-dorogi',
                                                              'derevyannye-zheleznie-dorogi',
                                                              'elektricheskie',
                                                              'katera-na-ru',
                                                              'mashiny',
                                                              'mashinki'
                                                              'transformery-mashiny',
                                                              'bolshie-mashiny',
                                                              'samolety-i-vertolety',
                                                              'tanki',
                                                              'kosmicheskie-korabli',
                                                              'radioupravlenii',
                                                              'syuzhetno-rolevye-igry',
                                                              'kukolnyy-teatr',
                                                              'detskie-kuhni',
                                                              'bytovaya-tehnika',
                                                              'igrushechnaya-posuda',
                                                              'detskiy-supermarket',
                                                              'igrushechnoe-oruzhie',
                                                              'masterskaya',
                                                              'shpionskie-shtuchki',
                                                              'ukrasheniya-i-aksessuary',
                                                              'zhivotnye',
                                                              'hasbro-furreal-friends',
                                                              'digibirds',
                                                              'furby',
                                                              'little-live-pets',
                                                              'ptichki',
                                                              'roborybki',
                                                              'letayuschie-fei',
                                                              'detskie-kompyutery',
                                                              'igrushechnye-telefonchiki',
                                                              'robot'
                                                              'geroi-multfilmov',
                                                              'chi-chi-love',
                                                              'aktivnye-igry',
                                                              'domiki-palatki',
                                                              'hranenie-igrushek',
                                                              'tvister',
                                                              'myachi',
                                                              'popryguny',
                                                              'bouling',
                                                              'golf',
                                                              'darts',
                                                              'nastolnyy-futbol',
                                                              'nastolnyy-hokkey',
                                                              'igrovye'
                                                              'igrushechnye-zhivotnye',
                                                              'dinozavry',
                                                              'novinki',
                                                              'dlya-malchikov',
                                                              'dlya-devochek',
                                                              'brendy-igrushek',
                                                              'lego',
                                                              'bruder',
                                                              'hasbro',
                                                              'baby-alive',
                                                              'descendants',
                                                              'kre-o',
                                                              'plastilin-play-doh',
                                                              'playskool',
                                                              'jurassic-world',
                                                              'trolls',
                                                              'dohvinci',
                                                              'polesie',
                                                              'bright-starts',
                                                              'spin-master',
                                                              'toys'
                                                              'keenway',
                                                              'brendy-igrushek',
                                                              'obuchenie-i-tvorchestvo',
                                                              '3d-ruchki',
                                                              'mylovarenie-kosmetika',
                                                              'mylo-ruchnoy-raboty',
                                                              'kosmetika',
                                                              'izgotovlenie-svechey',
                                                              'yunyy-parfyumer',
                                                              'detskaya-kosmetika-i-bodi-art',
                                                              'vyrashivanie-rasteniy',
                                                              'lepka-i-zhivoi-pesok',
                                                              'plastilin',
                                                              'zhivoy-pesok',
                                                              'pesochnitsy',
                                                              'kartiny-iz-plastilina',
                                                              'massa-dlya-lepki',
                                                              'testo-dlya-lepki',
                                                              'lepka-barelief',
                                                              'podelki',
                                                              'applikatsiya',
                                                              'vyzhiganie',
                                                              'gravyura',
                                                              'dekupazh',
                                                              'kartiny',
                                                              'folga-i-metall',
                                                              'mozaika-smalta',
                                                              'obemnye-podelki',
                                                              'pikselnaya-mozaika',
                                                              'podelki-iz-bumagi',
                                                              'freska-panno-smalta',
                                                              'kormushki-dlya-ptits-svoimi-rukami',
                                                              'doski-dlya-risovaniya',
                                                              'planshety-dlya-risovaniya',
                                                              'molberty',
                                                              'rospis-po-holstu',
                                                              'rospis',
                                                              'mandala-raskraska-antistress',
                                                              'risovanie-po-trafaretam',
                                                              'rukodelie',
                                                              'ukrasheniya-svoimi-rukami',
                                                              'braslety-iz-rezinok',
                                                              'valyanie',
                                                              'vyshivka',
                                                              'vyazanie',
                                                              'pletenie',
                                                              'shitie',
                                                              'yunyy-kulinar',
                                                              'nakleyki-na-odezhdu',
                                                              'brendy-obuchenie-i-tvorchestvo',
                                                              '4m',
                                                              'lori',
                                                              'kineticheskiy-pesok-lori',
                                                              'plastilin-lori',
                                                              'podelki-lori',
                                                              'freski-lori',
                                                              'markwins',
                                                              'style-me-up',
                                                              'azbukvarik',
                                                              'volshebnaya-masterskaya',
                                                              'vyrasti-derevo',
                                                              'cra-z-art',
                                                              'brendy-obuchenie-i-tvorchestvo',
                                                              'igry-i-obuchenie',
                                                              'globusy',
                                                              'mikroskopy-teleskopy',
                                                              'mikroskopy',
                                                              'teleskopy',
                                                              'nauka-i-opyty',
                                                              'diaproektory-i-diafilmy',
                                                              'nakleyki',
                                                              'obuchayuschie',
                                                              'elektro'
                                                              'uchim'
                                                              'sport',
                                                              'begovely',
                                                              'samokaty',
                                                              'sanki',
                                                              'ledyanki',
                                                              'snoutyuby',
                                                              'lopati-i-snezhkolepi',
                                                              'lopaty',
                                                              'snoubordy',
                                                              'termosy',
                                                              'termosumki',
                                                              'butylki-dlya-vody',
                                                              'velosipedy',
                                                              'rolikovye-konki',
                                                              'igry-na-ulitse',
                                                              'vse-dlya-kupaniya',
                                                              'krugi',
                                                              'narukavniki',
                                                              'naduvnye-myachi',
                                                              'vozdushnye-zmei',
                                                              'naduvnie',
                                                              'mylnye-puzyri',
                                                              'badminton',
                                                              'basketbol',
                                                              'gorki-detskie',
                                                              'kacheli',
                                                              'skakalki',
                                                              'zaschita',
                                                              'skeytbordy',
                                                              'mashiny-s-pedalyami',
                                                              'giroskuter',
                                                              'nasosy',
                                                              'brendy-sport',
                                                              '21st-scooter',
                                                              'explore',
                                                              'fox-pro',
                                                              'intex',
                                                              'hipe',
                                                              'hobby-bike',
                                                              'limit',
                                                              'moby-kids',
                                                              'brendy-sport',
                                                              'kolyaski-i-avtokresla',
                                                              'avtokresla',
                                                              'gruppa',
                                                              'bustery-18-36-kg',
                                                              'bazy-dlya-avtokresel',
                                                              'avtoaksessuary',
                                                              'chehly',
                                                              'nakidki-dlya-zaschity-avtomobilnogo-sidenya',
                                                              'detskie-podgolovniki',
                                                              'nedorogie-avtokresla',
                                                              'detskie-kolyasky',
                                                              'kolyaski-trosti',
                                                              'progulochnye-kolyaski',
                                                              'kolyaski'
                                                              'lyulki',
                                                              'aksessuary-dlya-detskih-kolyasok',
                                                              'dozhdeviki',
                                                              'moskitnye-setki',
                                                              'podnozhki-dlya-vtorogo-rebenka',
                                                              'zamki-dlya-kolyaski',
                                                              'sumki-dlya-mamy',
                                                              'komplekty-aksessuarov',
                                                              'adaptery-dlya-kolyasok',
                                                              'kolesa-dlya-kolyasok',
                                                              'mufty',
                                                              'komplekt-remney',
                                                              'kolyaski-dlya-puteshestviy',
                                                              'progulochnye-kolyaski-dlya-novorozhdennyh',
                                                              'brendy-kolyasok-i-avtokresel',
                                                              'babyhit',
                                                              'baby-design',
                                                              'britax-roemer',
                                                              'cam',
                                                              'brand-chicco',
                                                              'cybex',
                                                              'espiro',
                                                              'fd-design',
                                                              'brendy-kolyasok-i-avtokresel',
                                                              'dlya-novorozhdennyh',
                                                              'konverty-dlya-novorozhdennyh',
                                                              'zimnie-konverty',
                                                              'demisezonnye-konverty',
                                                              'letnie-konverty',
                                                              'konverty-na-vypisku',
                                                              'konverty-dlya-kolyasok',
                                                              'stulchiki-dlya-kormleniya',
                                                              'semnye-stoliki-dlya-stulchikov',
                                                              'chehly-dlya-stulchikov-dlya-kormleniya',
                                                              'manezhi',
                                                              'shezlongi-kacheli',
                                                              'detskie-shezlongi',
                                                              'videonyani',
                                                              'radionyani',
                                                              'podguzniki',
                                                              'zdorovye-i-uhod',
                                                              'aspiratory',
                                                              'zubnye-schetki',
                                                              'rascheski',
                                                              'detskie-termometry',
                                                              'vesy',
                                                              'detskie-grelki',
                                                              'mashinki-dlya-strizhki',
                                                              'braslety-ot-komarov',
                                                              'gazootvodnye-trubki',
                                                              'tonometry',
                                                              'nebulayzery-ingalyatory',
                                                              'dlya-kupaniya',
                                                              'gubki',
                                                              'mochalki',
                                                              'kovshiki-dlya-vanny',
                                                              'organayzery-dlya-vanny',
                                                              'zaschitnye-kozyrki',
                                                              'kovriki-v-vannu',
                                                              'krugi-dlya-kupaniya',
                                                              'termometry-dlya-vody',
                                                              'sideniya',
                                                              'detskoe-kormlenie',
                                                              'butilochki-dlya-kormleniya',
                                                              'soski-dlya-butilochek',
                                                              'aksessuary-dlya-kormlenija',
                                                              'pustyshki',
                                                              'niblery',
                                                              'poilniki',
                                                              'nagrudniki',
                                                              'posuda-detskaya',
                                                              'sterilizatory',
                                                              'podogrevateli',
                                                              'parovarki-blendery',
                                                              'dlya-mam',
                                                              'molokootsosy',
                                                              'nakladki-vkladyshi-dlya-grudi',
                                                              'sbor-i-hranenie-grudnogo-moloka',
                                                              'termosumki-konteineri',
                                                              'gigiena',
                                                              'salfetki',
                                                              'gorshki',
                                                              'sidenya-na-unitaz',
                                                              'kleenki',
                                                              'vatnye-palochki',
                                                              'detskaya-zaschita',
                                                              'blokiruyuschie-ustroystva',
                                                              'detskaya-mebel',
                                                              'pelenalnye-stoliki',
                                                              'kolybeli',
                                                              'kreslitse-pufy',
                                                              'bariery',
                                                              'v-detskuyu',
                                                              'uvlazhniteli-vozduha',
                                                              'shtory',
                                                              'stoly-i-stulya',
                                                              'kovry-dlya-detskoy',
                                                              'brendy-novorozhdennym',
                                                              'roxy-kids',
                                                              'lubby',
                                                              'handypotty',
                                                              'pocketpotty',
                                                              'philips-avent',
                                                              'ergopower',
                                                              'pigeon',
                                                              'nuk',
                                                              'brendy-novorozhdennym',
                                                              'komplekty-v-krovatku',
                                                              'postelnoe',
                                                              'spalnoe'
                                                              'bortiki-v-krovatku',
                                                              'prostyni',
                                                              'namatrasniki',
                                                              'polotentsa',
                                                              'odeyala',
                                                              'detskie-pledy',
                                                              'pokryvala',
                                                              'podushki',
                                                              'komplekty-postelnogo-belya',
                                                              'matrasy',
                                                              'dessert',
                                                              'autlet',
                                                              'obuchenie-i-tvorchestvo',
                                                              'igry-i-obuchenie',
                                                              'sport',
                                                              'kolyaski-i-avtokresla',
                                                              'dlya-novorozhdennyh',
                                                              'dessert',
                                                              'product-of-the-day',
                                                              'autlet',
                                                              'new-year',
                                                              'kuoma',
                                                              'luce-della-vita-gino-de-luka-desert',
                                                              'kvadrokoptery',
                                                              'poli-robokar',
                                                              'zheleznye-dorogi',
                                                              'radioupravlyaemye-mashinki',
                                                              'geroi-v-maskah',
                                                              'boom-by-orby',
                                                              'huppa',
                                                              'lassie',
                                                              'oldos',
                                                              'dakottakids',
                                                              'didriksons',
                                                              'premont',
                                                              'ma-zi-ma',
                                                              'alasca-originale',
                                                              'bopy',
                                                              'bottilini',
                                                              'dandino',
                                                              'elegami',
                                                              'flamingo',
                                                              'geox',
                                                              'kuoma',
                                                              'roxy-kids',
                                                              'lubby',
                                                              'handypotty',
                                                              'pocketpotty',
                                                              'philips-avent',
                                                              'ergopower',
                                                              'pigeon',
                                                              'nuk',
                                                              'lego',
                                                              'bruder',
                                                              'hasbro',
                                                              'polesie',
                                                              'bright-starts',
                                                              'spin-master',
                                                              'keenway',
                                                              'detskaya-kosmetika-i-bodi-art',
                                                              'magnitnye',
                                                              'nastolnye-igry'
                                                              ])

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
                'futbolki'
            ])

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
