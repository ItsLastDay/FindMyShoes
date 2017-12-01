import os
import pathlib
import json
from common import default_raw_dir

from data_extractor import extract_and_write_json

# https://kctati.ru/catalog/botilony/botilony_cupage_11/
# _product##zebra-12027-1-sapogi-shkolnye-uteplennye-12-par-v-kor.html
# www.wildberries.ru/_catalog##1008827##detail.aspx.html # https://www.wildberries.ru/catalog/1008827/detail.aspx
# www.wildberries.ru/_catalog##1151338##detail.aspx.html
# https://my-shop.ru/shop/products/1359627.html
# my-shop.ru/_shop##products##2847365.html.meta
# http://www.top-shop.ru/product/1936663-trend-myagkost-cvet-seryy/ # www.top-shop.ru/_product##1936663-trend-myagkost-cvet-seryy##.html
# www.top-shop.ru/_product##146455-bradex-pedikyur##.meta
# www.top-shop.ru/_product##380547-walkmaxx-snow-boots##.meta
# www.ozon.ru/_context##detail##id##140430339##.html

if __name__ == '__main__':
    # load file.
    start = 0
    meta_names = ['kctati.ru/_catalog##botilony##botilony_cupage_11##.meta',
                  'www.kinderly.ru/_product##zebra-12027-1-sapogi-shkolnye-uteplennye-12-par-v-kor.meta',
                  'www.wildberries.ru/_catalog##1008827##detail.aspx.meta',
                  'www.wildberries.ru/_catalog##1151338##detail.aspx.meta',
                  'my-shop.ru/_shop##products##1359627.html.meta',
                  'my-shop.ru/_shop##products##2847365.html.meta',
                  'www.top-shop.ru/_product##380547-walkmaxx-snow-boots##.meta',
                  'www.ozon.ru/_context##detail##id##140430339##.meta'
                  ][start:]
    meta_files = [os.path.join(default_raw_dir(), meta_name) for meta_name in meta_names]
    extraction_results = [
                             {
                                 'shop': 'kctati.ru',
                                 'url': 'https://kctati.ru/catalog/botilony/botilony_cupage_11/',
                                 'size': 67160,
                                 'name': 'Ботильоны женские CUPAGE',
                                 # 'description': 'Ботильоны Cupage спасут вас от низких температур и окружат теплом и уютом на многие годы. '
                                 #                'Натуральная кожа и прочная текстура идеально сядут на ногах. '
                                 #                'С черным классическим цветом вы сможете комбинировать туфли с каким угодно видом одежды. '
                                 #                'Необычная вставка сделает дизайн очень стильным, поэтому вы без труда привлечете восторженные взгляды окружающих. '
                                 #                'Устойчивые каблуки не позволят вам упасть, а мягкие стельки защитят от мозолей и усталости. '
                                 #                'Прочтите ботильоны Cupage отзывы и убедитесь в достоверности вышеуказанной информации.',
                                 'brand': 'Россия',
                                 'image': 'http://kctati.ru/upload/iblock/3c4/3c4ef9d8a437d7849478c78d3bd36b60.jpg',
                                 'price': 7290,
                                 'colors': ['Черный'],
                                 'hash': '8852b59e2e59bed9803dd47b0d3e4a92',
                                 'attributes': {'Обхват голенища макс. р-ра': '37',
                                                'Артикул': 'УТ-00030101',
                                                'Высота голенища макс. р-ра': '22',
                                                'Обхват голенища 37 р-ра': '35',
                                                'АртикулПроизводителя': 'D88-3-M8',
                                                'Страна производитель': 'Россия',
                                                'Сезон': 'Зима',
                                                'Материал подкладки': 'Мех натуральный',
                                                'Полнота': '8',
                                                'Высота голенища 37 р-ра': '20',
                                                'Высота каблука': '5',
                                                'Материал стельки': 'Мех натуральный',
                                                'Бренд': 'CUPAGE',
                                                'Обхват щиколотки 37 р-ра': '32',
                                                'Материал верха': 'Замша нат.+кожа'},
                                 # 'sizes': [35, 36, 37, 38, 39, 40],
                                 'type': 'Ботильоны',
                                 'gender': 'Ж'
                             },
                             {
                                 'sizes': [32, 33, 34, 35, 36, 37], 'price': 3090, 'size': 335483,
                                 'reviews': [
                                     'Добрый день, просьба сообщить сколько весят ботинки и какова длина стельки, \n\nспасибо,'],
                                 'brand': 'Зебра', 'name': 'Ботинки Зебра мембрана, зимние ', 'shop': 'www.kinderly.ru',
                                 'image': 'https://static.kinderly.ru/images/products/1/4166/33517638/_MG_1261.JPG',
                                 'colors': ['черные'], 'gender': 'M',
                                 'attributes': {'Подошва': ',', 'Стелька': 'Искусственная кожа',
                                                'Сезон': 'Защищенный мыс',
                                                'Страна бренда': 'Микрофибра', 'Особенности обуви': ',',
                                                'Вид ботинок/сапог': 'Высокие',
                                                'Страна изготовитель': 'Натуральная шерсть',
                                                'Внутренний материал': 'от +5°до -20°С',
                                                'Внешний материал обуви': 'Зима',
                                                'Температурный режим': 'Осень-Зима 2017-2018', 'Тип застежки': ',',
                                                'Назначение обуви': 'Анатомическая', 'Пол': 'Натуральная шерсть',
                                                'Коллекция': 'С утяжкой'},
                                 'url': 'http://www.kinderly.ru/product/zebra-12027-1-sapogi-shkolnye-uteplennye-12-par-v-kor',
                                 'hash': '510cc17f0cd00bffc0dd5e81709b1e88', 'type': 'Ботинки',
                                 'description': 'Чтобы ножке ребенка всегда было комфортно, тепло и сухо, поздней осенью и ранней весной; '
                                                'зимой, при температурном режиме до -20, ТМ «ЗЕБРА» разработала и предлагает в своих коллекциях обувь '
                                                'с высокотехнологичной мембраной, которая практически исключает вероятность простуды у детей, '
                                                'т.к. обладает долговременной водонепроницаемостью,одновременно, позволяя ножке дышать, тем самым, '
                                                'сохраняя оптимальный микроклимат внутри. Материал подошвы: Полимерный материал (Филон/ТЭП)'
                             },
                             {
                                 'type': 'сабо',
                                 'description': 'Удобные сабо на нескользящей подошве из уникального материала, запатентованной разработки бренда, '
                                                'который поглощает ударную силу при ходьбе и снижает негативную нагрузку на позвоночник. '
                                                'Благодаря вентиляционным отверстиям комфортно в такой обуви при большой амплитуде температур. '
                                                'Тип модели по полноте - Roomy fit. Классическая форма Crocs, обеспечивающая максимальный комфорт. '
                                                'При необходимости можно носить с носками любой плотности.  '
                                                'Эти модели отличаются увеличенной длиной - пальцы не упираются в носок обуви. '
                                                'Максимальная защита.  Максимальная полнота - стопа практически не соприкасается со стенками обуви. '
                                                'Обувь Roomy fit отличается высоким подъемом -'
                                                'сверху стопы достаточно пространства для обеспечения свободной циркуляции воздуха.',
                                 'attributes': {'Вид застежки': 'Без застежки', 'Материал стельки': 'без стельки',
                                                'Сезон': 'лето', 'Страна бренда': 'Соединенные Штаты',
                                                'Материал подошвы обуви': 'резина; croslite',
                                                'Материал подкладки обуви': 'Без подкладки',
                                                'Габариты предмета (см)': 'высота подошвы: 1 см',
                                                'Форма мыска': 'круглый',
                                                'Назначение обуви': 'повседневная', 'Вид мыска': 'закрытый',
                                                'Пол': 'Женский', 'Комплектация:': 'сабо',
                                                'Вид каблука': 'платформа; без каблука',
                                                'Страна производитель': 'Китай'},
                                 'sizes': [40, 41, 42, 43],
                                 'url': 'https://www.wildberries.ru/catalog/1008827/detail.aspx',
                                 'name': 'Сабо Classic',
                                 'size': 76761, 'hash': '63d3fb06ce26f83d9ab1910627ee30b0', 'colors': ['розовый'],
                                 'gender': 'Ж', 'shop': 'www.wildberries.ru',
                                 'brand': 'CROCS',
                                 'image': 'http://img1.wbstatic.net/large/new/1000000/1008827-1.jpg', 'price': 1550
                             },
                             {
                                 'attributes': {
                                     'Материал подкладки обуви': 'Текстиль',
                                     'Вид каблука': 'платформа',
                                     'Сезон': 'круглогодичный',
                                     'Комплектация:': 'пинетки',
                                     'Пол': 'Малыши',
                                     'Материал подошвы обуви': 'полиуретан',
                                     'Страна бренда': 'Соединенные Штаты',
                                     'Страна производитель': 'Китай'
                                 },
                                 'name': 'Пинетки',
                                 'brand': 'Luvable Friends',
                                 'type': 'пинетки',
                                 'url': 'https://www.wildberries.ru/catalog/1151338/detail.aspx',
                                 'size': 75312,
                                 'shop': 'www.wildberries.ru',
                                 'colors': [
                                     'темно-синий',
                                     'оранжевый',
                                     'белый'
                                 ],
                                 'image': 'http://img2.wbstatic.net/large/new/1150000/1151338-1.jpg',
                                 'hash': '81f3791fd0ff497ec53496ad549c3239', 'sizes': [],
                                 'description': 'Высокие кеды-пинетки "Зигзаг" на липучке для мальчика. '
                                                'Стильная модель с нескользящей подошвой. '
                                                'Мягкая резинка-шнурок не сдавливает ножку малыша, '
                                                'способствует ее правильному формированию.',
                                 'price': 590,
                                 'gender': 'М'
                             },
                             {
                                 'name': 'Тапочки с "памятью" "Комфорт"',
                                 'shop': 'my-shop.ru',
                                 'hash': '0493c18bf232d3b172833f015cadb723',
                                 'attributes': {
                                     'стандарт': '24 шт.',
                                     'артикул у производителя': 'KZ 0020',
                                     'код системы скидок': '25',
                                     'материал': 'ПВХ, велюр',
                                     'код в My-shop.ru': '1359627',
                                     'упаковка': '320x240x90 мм'},
                                 'image': 'http://static.my-shop.ru/product/2/136/1359627.jpg',
                                 'reviews': [
                                     'Размер 37, не больше. Мягкие, удобные.',
                                     'Размер по стельке 24,5 см. У меня длина стопы 24,5,'
                                     ' но пятка упирается в валик сзади, '
                                     'хочется, чтобы еще был запас. Через несколько минут ногам жарко.'],
                                 'price': 674,
                                 'url': 'https://my-shop.ru/shop/products/1359627.html',
                                 'sizes': [37, 38, 39],
                                 'size': 41536
                             },
                             {
                                 'shop': 'my-shop.ru',
                                 'url': 'https://my-shop.ru/shop/products/2847365.html',
                                 'hash': 'e64f6ef1715c3ee3e6b71afca7299cdf',
                                 'size': 28149,
                                 'name': 'Полуботинки "Worker. Траффик',
                                 'image': 'http://static.my-shop.ru/product/2/285/2847365.jpg',
                                 'sizes': [44.0],
                                 'price': 1645,
                                 'attributes': {
                                     'цвет': 'черный',
                                     'код системы скидок': '25',
                                     'код в My-shop.ru': '2847365',
                                     'материал': 'полиуретан, кожа',
                                     'страна изготовления': 'Россия',
                                     'артикул у производителя': '9401'
                                 }
                             }
                             ,
                             {
                                 'image': 'http://cdn2.top-shop.ru/ee/d4/normal_68550eaa6a7e8dcfccdd017dffa3d4ee.JPG',
                                 'price': 5999,
                                 'size': 95424,
                                 'brand': 'Walkmaxx',
                                 'name': 'Сапоги зимние Walkmaxx Snow Boots',
                                 'shop': 'www.top-shop.ru',
                                 'url': 'http://www.top-shop.ru/product/380547-walkmaxx-snow-boots/',
                                 'description': 'В чём плюсы этих сапог? Стильный зимний дизайн '
                                                'Флисовая подкладка удерживает тепло Влагостойкая мембрана '
                                                'сохраняет ваши ноги в сухости и комфорте Округлая подошва позволяет '
                                                'вам быть в тонусе и быстрее сжигать калории во время прогулок '
                                                'Комфортно, стильно, тепло Эта пара зимних сапог на шнурках идеально подходит всем, '
                                                'кто собирается бросить вызов зимней погоде!'
                                                ' Сапожки будут мягко удерживать ваши ноги благодаря флисовой подкладке, '
                                                'которая отлично сохраняет тепло.\xa0 '
                                                'А чтобы ваши ноги оставались сухими в слякотную погоду, '
                                                'в сапогах Walkmaxx предусмотрена влагостойкая мембрана для максимально комфортных прогулок. '
                                                'Стильный дизайн – блестящая стёганая поверхность прекрасно сочетается с симпатичными манжетами из искусственного меха. '
                                                'Эти зимние ботинки Вокмакс станут изюминкой вашего гардероба! Будьте в форме даже зимой! '
                                                'Зима – не повод отказывать себе в прогулках, особенно в зимних сапожках Walkmaxx: '
                                                'их округлая подошва будет держать вас в тонусе, а ходьба по снегу будет '
                                                'напоминать ходьбу по мягкому песку! Стопа в сапогах Walkmaxx '
                                                'перекатывается с пятки на носок, усиливается циркуляция крови. '
                                                'Нагрузка перераспределяется с суставов на мышцы. '
                                                'Без сознательных усилий с вашей стороны сапоги Walkmaxx помогают вам: '
                                                'Улучшать осанку, предотвращать боли в спине и суставах '
                                                'Перераспределить напряжение с суставов на мышцы '
                                                'Улучшать тонус и укреплять мышцы бедер, ягодиц, икр '
                                                'Сжигать больше калорий и терять вес быстрее '
                                                'Поверхность сапог изготовлена из качественного полиуретана, '
                                                'а подкладка сшита из мягкого флиса. '
                                                'Нескользящая подошва из микса ЭВА и резины успешно амортизирует удары при контакте с землей. '
                                                'Закажите Walkmaxx Snow Boots прямо сейчас, '
                                                'и получайте удовольствие от комфортных прогулок в зимнее время!',
                                 'hash': '7b37d43fa194799f6ba5ac4dcb5dea7f'
                             },
                             {
                                 'hash': '2b0f1718d91fe66ed2821f3dc6f391ea',
                                 'size': 117808,
                                 'shop': 'www.ozon.ru',
                                 'image': 'http://ozon-st.cdn.ngenix.net/multimedia/boots/1018405311.jpg',
                                 'sizes': [36],
                                 'brand': 'Inblu',
                                 'name': 'Сабо Inblu',
                                 'gender': 'Ж',
                                 'colors': ['черный', 'серебристый'],
                                 'description': 'Эффектные сабо от Inblu подчеркнут вашу смелую натуру! '
                                                'Модель выполнена из искусственной кожи. '
                                                'Стелька из искусственной кожи комфортна при движении. '
                                                'Высокая танкетка компенсирована платформой. '
                                                'Подошва дополнена рифлением.',
                                 'url': 'http://www.ozon.ru/context/detail/id/140430339/',
                                 'price': 3444
                             }
                         ][start:]

    def compare_lists(first, second):
        for f in first:
            if not f in second:
                print("{} is absent in expected".format(f))
        for s in second:
            if not s in first:
                print("{} is absent in json_data".format(s))

    def compare_dictionaries(json_data, expected):
        if json_data == expected:
            return
        if json_data.keys() != expected.keys():
            # print(prefix + 'Differs in keys:'.format(json_data.keys(), expected.keys()))
            # print(compare_lists(json_data.keys(), expected.keys()))
            print(json_data, "!= ", expected)
        elif len([None for key in json_data.keys() if json_data.get(key) != expected.get(key)]) <= 3:
            print(prefix + ": ")
            for key in json_data.keys():
                json_data_value = json_data.get(key)
                expected_value = expected.get(key)
                if json_data_value != expected_value:
                    if type(json_data_value) != type(expected_value):
                        print(' differ in key {} with types: {} != {}'.format(key, json_data_value, expected_value))
                    elif type(json_data_value) == dict:
                        print(' differ in key "{}":'.format(key))
                        compare_dictionaries(json_data_value, expected_value)
                    elif type(json_data_value) == list:
                        print(' differ in key "{}:'.format(key))
                        compare_lists(json_data_value, expected_value)
                    else:
                        print(' differ in key "{}": {} != {}'.format(key, json_data_value, expected_value))

    for i, meta_path in enumerate(meta_files):
        meta_file = pathlib.Path(meta_path)
        output_path = extract_and_write_json(meta_file, "/tmp/")
        with output_path.open() as output_file:
            json_data = json.load(output_file)
            expected = extraction_results[i]
            if json_data != expected:
                # TODO compare json_data with expected field-wise if difference is not so vast.
                prefix = '[FAIL] {} '.format(meta_names[i])
                compare_dictionaries(json_data, expected)
            else:
                print("[ OK ] {} ".format(meta_names[i]))
