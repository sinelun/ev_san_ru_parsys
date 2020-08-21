from .grabber import Grabber
from ..models import Parsing, Site, SitePage, SitePageParsing, SiteProductPage, SitePriceParsing


class ParseSite(Grabber):
    """ Класс управления процессом парсинга сайтов"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Id парсинга todo delete
        # self.parsing = kwargs['parser'] if 'parser' in kwargs else None

        self.parsing_type = kwargs['parsing_type'] if 'parsing_type' in kwargs else None
        if not self.parsing_type:
            raise Exception('Параметр "parsing_type" должен быть задан!')

        # URL сайта без '/' на конце
        self.site_url = kwargs['site_url'].rstrip('/') if 'site_url' in kwargs else None
        print("kwargs['site_url']: ", kwargs['site_url'])  # todo del
        # список URL-ов первого уровня, с которых начинается парсинг
        self.roots = kwargs['roots'] if 'roots' in kwargs else []
        # сохранять результаты парсинга в БД
        self.data_to_db = kwargs['data_to_db'] if 'data_to_db' in kwargs else True
        # выводить результаты в консоль
        self.print_data = kwargs['print_data'] if 'print_data' in kwargs else False

        # текущий парсинг todo продолжение оборванного парсинга
        latest_parsing = Parsing.objects.filter(type=self.parsing_type).latest('start')
        self.parsing = Parsing.objects.create(type=self.parsing_type) if latest_parsing.completed else latest_parsing
        # self.parsing, created = qs.get_or_create(id=self.parsing, completed=False)

        # текущий сайт
        print("self.site_url: ", self.site_url)  # todo del
        self.site, created = Site.objects.get_or_create(url=self.site_url)
        print('self.site.pk: ', self.site.pk)
        # текущая страница
        self.page = None
        # текущие данные парсинга
        self.data = {}
        # счётчик для отладки выводится только при печати в консоль
        self.counter = 0

        print(f'Parsing «{self.parsing}» has started...')

    def save_urls(self, urls, parent_level=None, flat=False):
        """ Сохраняет в SitePage новые URL-ы, обработанные check_url(url),
            создаёт новые записи в SitePageParsing.
            @flat: bool - True - парсинг продуктов; False - всего сайта
        """
        level = parent_level + 1 if parent_level is not None else 0
        for url in urls:
            url = self.check_url(url)
            # update_or_create важно вместо get_or_create, чтобы обновить поле updated
            site_page, created = SitePage.objects.update_or_create(site=self.site, url=url)
            SitePageParsing.objects.get_or_create(parsing=self.parsing, site_page=site_page, level=level)

    def parse_all_products(self):
        """ Парсинг всех продуктов, что уже спарсены
            FIXME
        """
        qs = SitePage.objects.filter(level=4) \
            .exclude(parsingpages__parsing=self.parsing, parsingpages__completed=True)
            # FIXME
            # .filter(... над последней сверху строкой должен быть фильтр по сопоставленным товарам...)

        for url in qs.values_list('url', flat=True):
            self.parse_product(url)

        return self.finish_parsing()

    # todo ...
    def parse_products(self, product_urls):
        for url in product_urls:
            self.parse_product(url)
        return self.finish_parsing()

    def parse_product(self, url):
        self.url = self.check_url(url)
        print(self.parsing, self.url)  # todo del

    def parse_site(self):
        """ Парсинг всего сайта с точки останова или краха.
        """
        print('Run parse_site()')
        # если ещё не существуют результаты текущего парсинга текущего сайта
        if not SitePageParsing.objects.filter(parsing=self.parsing, site_page__site=self.site):
            self.save_urls(self.roots)
        # Пока есть страницы, отмеченные, как незавершённые в текущем парсинге
        while SitePageParsing.objects.filter(parsing=self.parsing, site_page__site=self.site, completed=False):
            # первая страница в очереди на парсинг
            page_parsing = SitePageParsing.objects \
                .filter(parsing=self.parsing, site_page__site=self.site, completed=False) \
                .earliest('site_page__updated')
            self.page = page_parsing.site_page

            # Если у страницы уже есть html и она успешно подверглась текущему парсингу, её не надо "грабить" повторно;
            if self.page.html and SitePageParsing.objects \
                    .filter(parsing=self.parsing, site_page=self.page, completed=True):
                self.html = self.page.html
                self.make_soup()

            # ... иначе, попробовать спарсить текущую страницу
            else:
                if not self.grab_url(self.page.url):
                    page_parsing.success = False
                    page_parsing.http = self.http
                    page_parsing.save()
                    continue

            # Граббер сам создаёт self.soup для дальнейшего разбора.

            # Имя метода, переопределённого в соответствующем классе парсинга, для соответствующего уровня...
            method = 'parse_level_' + str(page_parsing.level)
            # ... сам метод...
            f = getattr(self, method)
            # ... результаты вызова метода
            new_urls, completed, success, save_html = f()

            print(method, new_urls, completed, success, save_html)  # todo del

            # Обновить модели данных текущей страницы:
            # - SitePageParsing
            page_parsing.completed = completed
            page_parsing.success = success
            page_parsing.http = self.http
            page_parsing.save()
            # - SitePage
            self.page.html = self.html if save_html else ''
            self.page.level = page_parsing.level
            self.page.save()

            # Сохранить URL-ы c текущей страницы
            self.save_urls(new_urls, page_parsing.level)

        return self.finish_parsing()

    def parse_level_0(self):
        return [], False, False, False

    def parse_level_1(self):
        return [], False, False, False

    def parse_level_2(self):
        return [], False, False, False

    def parse_level_3(self):
        return [], False, False, False

    def parse_level_4(self):
        return [], False, False, False

    def __prepare_data(self):
        return {
            'site_page': self.page,
            'name': self.data['name'],
            'sku': self.data['sku'],
            'site_code': self.data['site_code'],
            'brand': self.data['brand'],
            'price': self.data['price'],
            'price_discount': self.data['old_price'],
        }

    def save_data(self):
        if self.data_to_db:
            self.save_to_db()
        if self.print_data:
            self.print()
        return True

    def save_to_db(self):
        """ Сохраняет данные парсинга продукта в таблицу модели SiteData
        """
        product_page, created = SiteProductPage.objects.update_or_create(
            site_page=self.page,
            defaults={
                'brand': self.data['brand'],
                'sku': self.data['sku'],
                'name': self.data['name'],
                'site_code': self.data['site_code']
            }
        )
        SitePriceParsing.objects.update_or_create(
            parsing=self.parsing,
            product=product_page,
            defaults={
                'price': self.data['price'],
                'price_discount': self.data['old_price'],
            }
        )

    def print(self):
        """Выводит данные парсинга в консоль"""
        self.counter += 1
        print('№ : ' + str(self.counter))
        print(self.__prepare_data())

    def finish_parsing(self):
        """Успешное завершение парсинга"""
        if self.data_to_db:
            self.parsing.completed = True
            self.parsing.save()
        print(f'...parser {self.parsing} is finished')
        return True



