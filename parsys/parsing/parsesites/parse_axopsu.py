from .parsesite import ParseSite
from ..models import BrandSite, BrandSiteMapping
import re

import logging
logger = logging.getLogger(__name__)


class ParseAxopSu(ParseSite):
    """ Парсинг нтернет-магазина сантехники AXOR
    """

    # Значения параметров по умолчанию (**kwargs)
    defaults = {
        'site_url': 'https://axop.su',  # адрес сайта магазина, подвергающегося парсингу
        'roots': ['/brand', ],  # корневые URL-ы

        # параметры для отладки
        'brands': None,  # бренды, которые будут парситься, если пустой, то будут парситься все сопоставленные бренды;
        'max_page_number': 0,  # максимальное количество страниц 3-го уровня, которые будут парситься (для тестов);
        'parse_sections': True,  # забирать ссылки "По разделам" со страницы бренда
        'parse_collections': True,  # забирать ссылки "По коллекциям" со страницы бренда

        # CSS селекторы уровней
        'soup_select_level_0':  'ul.letter_brands>li>a',
        'soup_select_level_1_1': 'div.filter_block[min_title="По разделу"] > .filter_info > .brands a',
        'soup_select_level_1_2': 'div.filter_block[min_title="По коллекциям"] > .filter_info > .brands a',
        'soup_select_level_2': '.pager a',
        'soup_select_level_3': '.product .info a',
        'soup_select_product': '.card_info',
        'soup_select_product_name': '.card_info .page_header_block h1',
    }

    def __init__(self, **kwargs):
        # обновление значений по-умолчанию значениями параметров без добавления
        self.defaults.update((k, kwargs[k]) for k in set(kwargs).intersection(self.defaults))
        # обновление параметров объектов обновлёнными значениями по-умолчанию
        self.__dict__.update(self.defaults)
        # преобразование имён брендов к нижнему регистру с удалением пробелов по краям
        self.brands = self.convert_brands(self.brands)

        # параметры передаваемые в родительский конструктор
        kwargs['site_url'] = self.site_url
        kwargs['roots'] = self.roots

        super().__init__(**kwargs)

    # def parse_site(self):
    #     return super().parse_site()

    def parse_level_0(self):
        """Парсинг брендов из раздела https://axop.su/brand, адрес которого задан в self.roots"""
        urls = []
        if self.brands:
            logger.debug(f'Задан парсинг по отдельным брендам. '
                         f'Будут парситься следущие бренды: -- {self.brands} --')
        else:
            # Если не задан парсинг по отдельным брендам, взять бренды сопоставленные в модели BrandSiteMapping
            brands = BrandSiteMapping.objects.select_related('site_brand').filter(site_brand__isnull=False)\
                                                .values_list('site_brand__name', flat=True)
            self.brands = self.convert_brands(brands)
            logger.debug(f'Парсинг по отдельным брендам не задан. '
                         f'Будут парситься бренды, сопоставленные в модели BrandSiteMapping: -- {self.brands} --')
        # Цикл по всем брендам на сайте...
        for brand in self.soup.select(self.soup_select_level_0):
            brand_name = brand.string.strip().lower()
            # (все бренды сайта записываются в модель BrandSite для помощи в сопоставлении брендов (BrandSiteMapping))
            BrandSite.objects.update_or_create(
                site=self.site,
                name=brand_name,
                defaults={
                    'url': self.check_url(brand['href'])
                }
            )
            # ... пропуская бренды, которых нет в списке заданных
            if brand_name not in self.brands:
                continue
            urls.append(brand['href'])
        logger.debug(f'Начинается парсинг {len(urls)} брендов: {urls}')
        return urls, True, bool(urls), False

    def parse_level_1(self):
        """ Парсинг страницы бренда, например https://axop.su/aquanet/
        """
        urls = []
        if self.parse_sections:
            for link in self.soup.select(self.soup_select_level_1_1):
                urls.append(link['href'])
        if self.parse_collections:
            for link in self.soup.select(self.soup_select_level_1_2):
                urls.append(link['href'])
        return urls, True, bool(urls), False

    def parse_level_2(self):
        """ Страницы в пагинаторе
        """
        # Самая первая страница в пагинаторе, даже если он отсутствует
        urls = [self.url]
        # Если не задан парсинг только одной страницы (при тестировании)
        if self.max_page_number != 1:
            page_links = self.soup.select(self.soup_select_level_2)
            if page_links:
                last_page = int(page_links[-1].string)
                # При тестировании с заданием максимального количества обрабатываемых страниц
                last_page = last_page if (not self.max_page_number) or (last_page < self.max_page_number) \
                                        else self.max_page_number
                for i in range(2, last_page):
                    logger.debug('Paginator page:', i)
                    urls.append(self.url.rstrip('/') + '/page_' + str(i))
        return urls, True, bool(urls), True

    def parse_level_3(self):
        """ Страницы с товарами
        """
        urls = []
        for link in self.soup.select(self.soup_select_level_3):
            urls.append(link['href'])
        return urls, True, bool(urls), False

    def parse_level_4(self):
        """ Товар
        """
        result = self.parse_product()
        return [], bool(result), result, False

    def parse_product(self, url=None):
        """ Парсинг товара по его url.
            При периодическом парсинге цен по заданию вызывается независимо .
        """

        # В случае независимого вызова (в том числе, тестового)
        if url:
            if not self.grab_url(url):
                logger.warning(f'Задан URL товара: {url}, который невозможно спарсить.')
                return None

        self.data['brand'] = ''
        self.data['url'] = self.url
        self.data['name'] = ''
        self.data['site_code'] = ''
        self.data['sku'] = ''
        self.data['price'] = 0
        self.data['old_price'] = 0

        # <div class="card_info">
        card_info = self.soup.select_one(self.soup_select_product)

        if not card_info:
            logger.warning(f'Не найден элемент <div class="card_info"> с инфо товара на странице {self.url}')
            return None

        # Наименование товара
        try:
            el = self.soup.select_one(self.soup_select_product_name)
            self.data['name'] = el.string.strip()
        except:
            self.data['name'] = ''
            logger.warning(f'Невозможно определить название товара на странице {self.url}')

        # Бренд
        try:
            el = card_info.find('div', string='Бренд:')
            el = el.parent.select_one('a')
            self.data['brand'] = el.string.strip()
        except:
            self.data['brand'] = ''
            logger.warning(f'Невозможно определить бренд товара на странице {self.url}')

        # Код товара на сайте
        try:
            el = card_info.find('span', string='Код:')
            el = el.find_parent('div')
            self.data['site_code'] = el.get_text().strip()[5:]
        except:
            self.data['site_code'] = ''
            logger.warning(f'Невозможно определить код товара на странице {self.url}')

        # Артикул
        try:
            el = card_info.find('div', string='Артикул:')
            el = el.find_next_sibling('span')
            self.data['sku'] = el.string.strip()
        except:
            self.data['sku'] = ''
            logger.warning(f'Невозможно определить артикул товара на странице {self.url}')

        # Цена товара (со скидкой, если скидка есть)
        try:
            el = card_info.select_one('div.price')
            self.data['price'] = self.clear_price(el.string)
        except:
            self.data['price'] = 0
            logger.warning(f'Невозможно определить цену товара на странице {self.url}')

        # Старая цена (цена без скидки)
        try:
            el = card_info.select_one('div.old_price')
            self.data['old_price'] = self.clear_price(el.string)
        except:
            self.data['old_price'] = 0
            logger.debug(f'Невозможно определить старую цену товара на странице {self.url}')

        return self.save_data()

    @staticmethod
    def clear_price(price):
        return int(re.sub(r'\D', '', price))

    @staticmethod
    def convert_brands(brands):
        """ Преобразует имена брендов к нижнему регистру.
        """
        if not brands:
            return brands
        return [x.strip().lower() for x in brands]


""" --- FACADE --- """


def parse_axop_su_site(**kwargs):
    """ Парсинг всего сайта
    """
    logger.debug(f'Запущена функция фасада parse_axop_su_site() - парсинг всего сайта с параметрами: -- {kwargs} -- ')

    kwargs.update({'parsing_type': 'sites'})
    p = ParseAxopSu(**kwargs)
    return p.parse_site()


def parse_axop_su_brands(brands, **kwargs):
    """ Парсинг отдельных (выделенных) брендов
    """
    logger.debug(f'Запущена функция фасада parse_axop_su_brands() - парсинг отдельных (выделенных) брендов: '
                 f'-- {brands} -- ')

    kwargs.update({'parsing_type': 'sites', 'brands': brands})
    p = ParseAxopSu(**kwargs)
    return p.parse_site()


""" ---- TESTS --- """


def parse_axop_su_test1():
    logger.info('== Start parser_axop_su_test1')
    logger.info('''Run parse_axop_su_site()''')
    return parse_axop_su_site()


def parse_axop_su_test2():
    logger.info('== Start parser_axop_su_test2')
    logger.info('''Run parse_axop_su_site(max_page_number=1)''')
    return parse_axop_su_site(max_page_number=1)


def parse_axop_su_test3():
    logger.debug('== Start parser_axop_su_test3')
    return parse_axop_su_brands(['ifo'], parse_collections=False, max_page_number=1)


def parse_axop_su_test4():
    print('== Start parser_axop_su_test4: FULL PARSING')
    p = ParseAxopSu(print_data=True)
    return p.parse_site()


def parse_axop_su_test5():
    print('== Start parser_axop_su_test5: PARSE SINGLE PRODUCT')
    p = ParseAxopSu()
    return p.parse_product('https://axop.su/item/smesitel_dlya_bide_grohe_tenso_32367/')


def parse_axop_su_tests():
    logger.debug('==== Start parse_axop_su_tests')
    # print('Test 1: ' + ('Yes' if parse_axop_su_test1() else 'No'))
    # print('Test 2: ' + ('Yes' if parse_axop_su_test2() else 'No'))
    print('Test 3: ' + ('Yes' if parse_axop_su_test3() else 'No'))
    # print('Test 4: ' + ('Yes' if parse_axop_su_test4() else 'No'))
    # print('Test 5: ' + ('Yes' if parse_axop_su_test5() else 'No'))


