from .parsesite import ParseSite
from ..models import BrandSite, BrandSiteMapping
import re


class ParseAxopSu(ParseSite):
    """
    Парсинг нтернет-магазина сантехники AXOR
    """

    site_default = 'https://axop.su'  # адрес сайта магазина, подвергающегося парсингу
    roots_default = ['/brand',]  # корневые URL-ы

    def __init__(self, **kwargs):
        """ **kwargs:
                site - адрес сайта;
                brands - бренды, которые будут парситься;
                max_page_number - максимальное количество страниц 3-го уровня, которые будут парситься (для тестов);
                parse_sections - забирать ссылки "По разделам" со страницы бренда
                parse_collections - забирать ссылки "По коллекциям" со страницы бренда
        """
        kwargs['site'] = kwargs['site'] if 'site' in kwargs else self.site_default
        kwargs['roots'] = kwargs['roots'] if 'roots' in kwargs else self.roots_default
        # Бренды, которые будут парсится
        self.brands = [x.strip().lower() for x in kwargs['brands']] \
            if 'brands' in kwargs and isinstance(kwargs['brands'], list) else None
        # Максимальное количество страниц пагинатора, которое будет парсится
        self.max_page_number = kwargs['max_page_number'] if 'max_page_number' in kwargs else 0
        # Парсить по разделам?
        self.parse_sections = kwargs['parse_sections'] if 'parse_sections' in kwargs else True
        # Парсить по коллекциям?
        self.parse_collections = kwargs['parse_collections'] if 'parse_collections' in kwargs else True
        super().__init__(**kwargs)

    def parse_site(self):
        return super().parse_site()

    def parse_level_0(self):
        """Парсинг брендов из раздела https://axop.su/brand, адрес которого задан в self.roots"""
        print('Level 0', self.url)
        urls = []
        # Если не задан парсинг по отдельным брендам...
        if not self.brands:
            # ... взять бренды сопоставленные в модели BrandSiteMapping
            brands = BrandSiteMapping.objects.filter(site=self.site) \
                                        .exclude(site_brand='').values_list('site_brand', flat=True)
            self.brands = [x.strip().lower() for x in brands]
        for brand in self.soup.select('ul.letter_brands>li>a'):
            brand_name = brand.string.strip().lower()
            # Все бренды сата записываются в модель BrandSite для помощи в сопоставлении брендов
            BrandSite.objects.update_or_create(
                site=self.site,
                name=brand_name,
                defaults={
                    'url': self.check_url(brand['href'])
                }
            )
            if brand_name not in self.brands:
                continue
            urls.append(brand['href'])
        print(f'Начинается парсинг {len(urls)} брендов: {urls}')
        return urls, True, bool(urls)

    def parse_level_1(self):
        """ Парсинг страницы бренда, например https://axop.su/aquanet/
        """
        print('Level 1', self.url)
        urls = []
        if self.parse_sections:
            for link in self.soup.select('div.filter_block[min_title="По разделу"] > .filter_info > .brands a'):
                urls.append(link['href'])
        if self.parse_collections:
            for link in self.soup.select('div.filter_block[min_title="По коллекциям"] > .filter_info > .brands a'):
                urls.append(link['href'])
        return urls, True, bool(urls)

    def parse_level_2(self):
        """ Страницы в пагинаторе
        """
        print('Level 2', self.url)
        # Сама страница - первая в пагинаторе, даже если он отсутствует
        urls = [self.url]
        if self.max_page_number != 1:
            page_links = self.soup.select('.pager a')
            if page_links:
                last_page = int(page_links[-1].string)
                # Следующая строка для тестирования с заданием максимального количества обрабатываемых страниц
                last_page = last_page if (not self.max_page_number) or (last_page < self.max_page_number) else self.max_page_number
                for i in range(2, last_page):
                    print('Paginator page:', i)
                    urls.append(self.url.rstrip('/') + '/page_' + str(i))
        return urls, True, bool(urls)

    def parse_level_3(self):
        """ Страницы с товарами
        """
        print('Level 3', self.url)
        urls = []
        for link in self.soup.select('.product a.name'):
            urls.append(link['href'])
        return urls, True, bool(urls)

    def parse_level_4(self):
        """ Товар
        """
        print('Level 4', self.url)
        result = self.parse_product()
        return [], result, result

    def parse_product(self):
        """ Парсинг товара по его url.
            Вызывается независимо при периодическом парсинге цен по заданию.
        """

        self.data['brand'] = ''
        self.data['url'] = self.url
        self.data['name'] = ''
        self.data['site_code'] = ''
        self.data['sku'] = ''
        self.data['price'] = 0
        self.data['old_price'] = 0

        card_info = self.soup.select_one('div.card_info')

        if not card_info:
            return None

        # Наименование товара
        el = card_info.h1
        if el:
            self.data['name'] = el.string.strip()

        # Бренд
        el = card_info.find('div', string='Бренд:')
        if el:
            el = el.find_next_sibling('span')
        if el:
            self.data['brand'] = el.string.strip()

        # Код товара на сайте
        el = card_info.find('span', string='Код:')
        if el:
            el = el.find_parent('div')
        if el:
            self.data['site_code'] = el.get_text().strip()[5:]

        # Артикул
        el = card_info.find('div', string='Артикул:')
        if el:
            el = el.find_next_sibling('span')
        if el:
            self.data['sku'] = el.string.strip()

        # Цена товара (со скидкой, если она есть)
        el = card_info.select_one('div.price')
        if el:
            self.data['price'] = self.clear_price(el.string)

        # Старая цена (цена без скидки)
        el = card_info.select_one('div.old_price')
        if el:
            self.data['old_price'] = self.clear_price(el.string)

        return self.save_data()

    @staticmethod
    def clear_price(price):
        return int(re.sub(r'\D', '', price))


""" ---- ТЕСТЫ --- """


def parse_axop_su_test1():
    print('-- Start parser_axop_su_test1')
    p = ParseAxopSu(brands=['aquanet'], print_data=True)
    return p.parse_site()


def parse_axop_su_test2():
    print('-- Start parser_axop_su_test2')
    print('''ParseAxopSu(brands=['aquanet'], max_page_number=1, print_data=True)''')
    p = ParseAxopSu(brands=['aquanet'], max_page_number=1, print_data=True)
    return p.parse_site()


def parse_axop_su_test3():
    print('-- Start parser_axop_su_test3')
    print('''ParseAxopSu(brands=['aquanet'], max_page_number=1, print_data=True)''')
    p = ParseAxopSu(brands=['franke'], parse_collections=False, max_page_number=1, print_data=True)
    return p.parse_site()


def parse_axop_su_test4():
    print('-- Start parser_axop_su_test4: FULL PARSING')
    p = ParseAxopSu(print_data=True)
    return p.parse_site()


def parse_axop_su_tests():
    print('-- Start parse_axop_su_tests')
    # print('Test 1: ' + ('Yes' if parse_axop_su_test1() else 'No'))
    # print('Test 2: ' + ('Yes' if parse_axop_su_test2() else 'No'))
    # print('Test 3: ' + ('Yes' if parse_axop_su_test3() else 'No'))
    print('Test 4: ' + ('Yes' if parse_axop_su_test4() else 'No'))


