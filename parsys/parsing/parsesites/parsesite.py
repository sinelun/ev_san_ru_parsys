from .grabber import Grabber
from ..models import Parsing, Site, SitePage, SitePageParsing, SiteProductPage, SitePriceParsing
from django.conf import settings
from usersettings.models import UserSetting

import logging
logger = logging.getLogger(__name__)


class ParseSite(Grabber):
    """ Класс управления процессом парсинга сайтов.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Тип парсинга, если не задан, то парсинг тестовый
        self.parsing_type = kwargs['parsing_type'] if 'parsing_type' in kwargs else None

        # Тестовый ли парсинг?
        self.test = not bool(self.parsing_type)

        if self.test:
            logger.warning(f'Парсинг запущен в тестовом режиме (self.test = -- {self.test} --), '
                           f'в котором не происходит записи в базу данных.')

        # Парсинг на хостинге - True, локально - False
        self.production = bool(settings.ALLOWED_HOSTS)
        if self.production:
            logger.info(f'Парсинг запускается на хостинге.')
        else:
            logger.info(f'Парсинг запускается локально.')

        # URL сайта без '/' на конце
        self.site_url = kwargs['site_url'].rstrip('/') if 'site_url' in kwargs else None

        # список URL-ов первого уровня, с которых начинается парсинг
        self.roots = kwargs['roots'] if 'roots' in kwargs else []
        logger.info(f'Парсинг начнётся со следующих URL-ов: -- {self.roots} -- .')

        # текущий парсинг и текущий сайт (в тестовом режиме имеют пустые значения)
        if self.test:
            self.parsing = None
            self.site = None
        else:
            # последний по дате начала парсинг, заданного типа
            latest_parsing = Parsing.objects.filter(type=self.parsing_type).latest('start')
            if latest_parsing.completed:
                logger.info(f'Нет незавершённых парсингов типа -- {self.parsing_type} -- '
                             f'будет создан новый парсинг.')
                self.parsing = Parsing.objects.create(type=self.parsing_type)
            else:
                logger.info(f'Парсинг -- {latest_parsing} -- не был завершён.')
                self.parsing = latest_parsing
            # Объект сайта получается или создаётся
            self.site, created = Site.objects.get_or_create(url=self.site_url)
            if created:
                logger.info(f'Был создан объект сайта -- {self.site} -- для парсинга.')

        # Количество страниц, парсящихся за одну сессию cron задания на хостинге, по умолчанию - 5
        ps_numpages = UserSetting.objects.filter(slug='ps_numpages').values_list('value', flat=True).first()
        self.number_of_pages_at_a_time = int(ps_numpages) if ps_numpages else 5
        logger.info(f'Количество страниц, парсящихся за одну сессию cron задания на хостинге (ps_numpages): '
                    f'-- {self.number_of_pages_at_a_time} -- ')

        # Начальные параметры:
        # --------------------
        # текущая страница
        self.page = None
        # текущие данные парсинга
        self.data = {}
        # счётчик количества записей для отладочной информации
        self.counter = 0

        logger.info(f'Начат парсинг № -- {self.parsing} -- типа -- {self.parsing_type} -- сайта -- {self.site_url} -- ')

    def save_urls(self, urls, parent_level=None, flat=False):
        """ Сохраняет в SitePage новые URL-ы, передаваемые в параметре-списке @urls,
            которые предварительно будут обработаны check_url(url),
            Создаёт новые записи в SitePageParsing для продолжения процесса парсинга.
            @urls: list - новые URL-ы
            @parent_level: int - уровень страницы, с которой взяты @urls
            @flat: bool - True - парсинг продуктов; False - всего сайта
        """

        if self.test:
            logger.warning(f'В тестовом режиме URLs: {urls} не записываются в базу данных.')
            return

        level = parent_level + 1 if parent_level is not None else 0
        logger.debug(f'В БД с уровнем -- {level} -- будут записаны URL-ы: -- {urls} --')
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
        """ FIXME """
        for url in product_urls:
            self.parse_product(url)
        return self.finish_parsing()

    def parse_product(self, url):
        """ FIXME """
        self.url = self.check_url(url)

    def parse_site(self):
        """ Парсинг всего сайта с точки останова или краха.
        """
        if self.test:
            logger.warning('Парсинг всего сайта функцией parse_site() не предназначен для запуска в тестовом режиме.')
            return

        logger.info('Запущен парсинг всего сайта parse_site()')
        # если ещё не существуют результаты текущего парсинга текущего сайта
        if not SitePageParsing.objects.filter(parsing=self.parsing, site_page__site=self.site):
            logger.info(f'Результатов парсинга -- {self.parsing} -- сайта -- {self.site} -- пока нет.')
            self.save_urls(self.roots)

        # QuerySet страниц, не прошедших парсинг
        qs_uncompleted_pages = SitePageParsing.objects.filter(parsing=self.parsing,
                                                              site_page__site=self.site,
                                                              completed=False)

        # Закончить текущий парсинг, если QuerySet пуст, нет страниц, отмеченных, как незвершённые (completed=False)
        if not qs_uncompleted_pages:
            logger.info('Вызван finish_parsing(), больше страниц, отмеченных, как незвершённые (completed=False)')
            return self.finish_parsing()

        # На хостинге парсить определённое количество страниц...
        if self.production:
            logger.info('На хостинге происходит парсинг следующих -- {self.number_of_pages_at_a_time} -- страниц...')
            for i in range(0, self.number_of_pages_at_a_time):
                self.parse_page(qs_uncompleted_pages)
            return False
        # ... иначе...
        else:
            # ... на локальной машине парсить пока есть страницы, отмеченные, как незавершённые в текущем парсинге
            logger.info('На локальной машине идёт парсинг всех необходимых страниц...')
            while qs_uncompleted_pages.first():
                self.parse_page(qs_uncompleted_pages)
            return self.finish_parsing()

    def parse_page(self, qs):
        """ Парсинг одной страницы в цикле парсинга всего сайта parse_site()
            @qs: QuerySet - страницы, отмеченные, как незавершённые в текущем парсинге
        """

        # первая страница в очереди на парсинг
        page_parsing = qs.earliest('site_page__updated')
        self.page = page_parsing.site_page

        logger.debug(f'Парсинг parse_page() страницы {self.page}')

        # Если у страницы уже есть html и она успешно подверглась текущему парсингу, её не надо "грабить" повторно;
        if self.page.html and SitePageParsing.objects \
                .filter(parsing=self.parsing, site_page=self.page, completed=True):
            logger.debug(f'HTML страницы -- {self.page} -- был получен заранее.')
            self.html = self.page.html
            self.make_soup()
        # ... иначе, попробовать спарсить текущую страницу...
        else:
            logger.debug(f'Попытка получить страницу -- {self.page} -- с помощью grab.')
            if not self.grab_url(self.page.url):
                # ... в случае неудачи, выйти, записав причины в базу данных
                logger.warning(f'Не удалось получить содержимое страницы -- {self.page} --.')
                page_parsing.success = False
                page_parsing.http = self.http
                page_parsing.save()
                return

        # Граббер сам создаёт self.soup для дальнейшего разбора.

        # Имя метода, переопределённого в соответствующем классе парсинга, для соответствующего уровня...
        method = 'parse_level_' + str(page_parsing.level)
        # ... сам метод...
        f = getattr(self, method)
        # ... результаты вызова метода вида parse_level_[L]()
        new_urls, completed, success, save_html = f()

        logger.debug(f'{method}() вернул - new_urls: {new_urls} | '
                    f'completed: {completed}, success: {success} | save_html: {save_html}')

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

    def save_data(self):
        """ Сохраняет данные парсинга продукта в таблицу модели SiteData,
            если не тестовый режим
            @:returns были ли сохранены данные в базу данных
        """
        result = False
        if not self.test:
            try:
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
                result = True
            except:
                result = False
        if result:
            self.counter += 1
            logger.debug(f'The data was successfully saved: -- {self.counter} : {self.data} --')
        else:
            logger.warning(f' Следующие данные не были сохранены: -- {self.data} --')
        return result

    def finish_parsing(self):
        """ Успешное завершение парсинга
        """
        if self.test:
            return False

        self.parsing.completed = True
        self.parsing.save()

        logger.debug(f'Parsing # -- {self.parsing} -- of -- {self.parsing.type} -- has finished.')
        return True



