from grab import Grab
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class Grabber:
    """ Обёртка над Grab c использованием BeautifulSoup."""

    def __init__(self, **kwargs):
        super().__init__()
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
            возваращает False в случае "неудачного" кода ответа сервера, иначе - True
        """
        self.url = self.check_url(url)
        resp = self.grab.go(url)
        self.http = resp.code
        if self.check_http():
            self.html = resp.unicode_body()
            self.make_soup()

        return bool(self.soup)

    def check_url(self, url):
        """ Просто подставляет адрес сайта к url-ам без него, пока без дополнительных проверок."""
        u = urlparse(url)
        if u.scheme:
            return url
        if self.site_url:
            return self.site_url + '/' + url.lstrip('/')
        raise Exception('Bad URL or site is not set')

    def check_http(self):
        """ Пока производит простейшую проверку статуса ответа. todo"""
        if self.http < 400:
            return True
        return False

    def make_soup(self):
        """ Получает "суп" из текущего HTML """
        self.soup = BeautifulSoup(self.html, 'lxml')


""" ---- ТЕСТЫ --- """


def grabber_test1():
    print('-- Start grabber_test1')
    g = Grabber('https://axop.su')
    print(g)
    success = g.run_grab('/vanny/')
    print(g.site, g.url, g.code, success)
    return g.site == 'https://axop.su' and \
           g.url == 'https://axop.su/vanny/' and \
           g.code == 200 and success is True


def grabber_tests():
    print('-- Start grabber_tests')
    print('Test 1: ' + ('Yes' if grabber_test1() else 'No'))

