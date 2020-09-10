from grab import Grab
from urllib.request import urlopen
from urllib.parse import urlparse
from bs4 import BeautifulSoup

import logging
logger = logging.getLogger(__name__)


class Grabber:
    """ Обёртка над Grab c использованием BeautifulSoup.
    """

    def __init__(self, **kwargs):
        # super().__init__() # todo возможно удалить...

        # URL сайта без '/' на конце
        self.site_url = kwargs['site_url'].rstrip('/') if 'site_url' in kwargs else None

        self.url = None  # текущий URL
        self.http = None  # текущий код HTTP ответа
        self.html = None  # текущий HTML ответа
        self.soup = None  # текущий "суп"
        grab_settings = kwargs['grab_settings'] if 'grab_settings' in kwargs else {}
        self.grab = Grab(**grab_settings)

    def grab_url(self, url):
        """ "Грабит" данные по url;
            принимает целые (с адресом сайта) и не целые (относительные) url-ы;
            устанавливает текущие свойства;
            возваращает False в случае неудачи, иначе - True
        """
        self.url = self.check_url(url)
        try:
            1/0
            resp = self.grab.go(self.url)
            self.http = resp.code
            self.html = resp.unicode_body()
        except Exception as ex:
            logger.debug(f'Невозможно получить данные с -- {self.url} -- c помощью grab по причине: {ex}')
            try:
                resp = urlopen(self.url)
                self.http = resp.getcode()
                self.html = resp
            except Exception as ex:
                logger.error(f'Невозможно вообще получить данные с -- {self.url} -- по причине: {ex}')
                return False
        if self.check_http():
            self.make_soup()
        return bool(self.soup)

    def check_url(self, url):
        """ Просто подставляет адрес сайта к url-ам без него,
            todo пока без дополнительных проверок.
        """
        u = urlparse(url)
        if u.scheme:
            return url
        if self.site_url:
            return self.site_url + '/' + url.lstrip('/')
        raise Exception('Bad URL or site is not set')

    def check_http(self):
        """ Производит простейшую проверку статуса ответа.
            todo сложнее
        """
        result = None
        if not self.http:
            result = False
        elif self.http < 400:
            result = True
        else:
            result = False
        if not result:
            logger.warning(f'Плохой статус ответа: -- {self.http} -- ')
        return result

    def make_soup(self):
        """ Получает "суп" из текущего HTML """
        self.soup = BeautifulSoup(self.html, 'lxml')


""" ---- ТЕСТЫ --- """


def grabber_test1():
    logger.debug('-- Start grabber_test1')
    g = Grabber(site_url='https://axop.su')
    logger.debug(f'''g = Grabber(site_url='https://axop.su') => -- {g} --''')
    success = g.grab_url('/vanny/')
    logger.debug(f'g.site_url: -- {g.site_url} --, g.url: -- {g.url} --, g.http: -- {g.http} --, success: -- {success} --')
    return g.site_url == 'https://axop.su' and \
           g.url == 'https://axop.su/vanny/' and \
           g.http == 200 and success is True


def grabber_tests():
    logger.debug('-- Start grabber_tests')
    logger.debug('Test 1: ' + ('Yes' if grabber_test1() else 'No'))
