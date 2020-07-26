from django.db import models
from .parsing import Parsing


class Site(models.Model):
    """ Сайты-доноры
    """

    url = models.URLField(unique=True, blank=False, verbose_name='Адрес источника')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Добавлен')
    updated = models.DateTimeField(auto_now=True, verbose_name='Запущен последний парсинг')

    def __str__(self):
        return self.url

    class Meta:
        verbose_name = 'Сайт'
        verbose_name_plural = 'Сайты'


class SitePage(models.Model):
    """ Страницы сайтов создаются один раз при первом проходе парсинга(ов),
        затем только обновляются. Для удаления всех - удалить сайты (Site).
    """

    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name='Сайт', related_name='pages')
    url = models.URLField(unique=True, verbose_name='Адрес страницы')
    html = models.TextField(null=True, blank=True, default=None, verbose_name='Последний HTML страницы')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Добавлен')
    updated = models.DateTimeField(auto_now=True, verbose_name='Оновлён')

    def __str__(self):
        return self.url

    class Meta:
        verbose_name = 'Страница сайта'
        verbose_name_plural = 'Страницы сайтов'


class SitePageParsing(models.Model):
    """ Техническая модель для процесса парсинга сайтов. """

    parsing = models.ForeignKey(Parsing, on_delete=models.CASCADE, verbose_name='Парсинг')
    site_page = models.ForeignKey(SitePage, on_delete=models.CASCADE, verbose_name='Страница сайта')
    level = models.SmallIntegerField(null=True, blank=True, default=None, verbose_name='Вложенность')
    http = models.SmallIntegerField(null=True, blank=True, default=None, verbose_name='HTTP-код ответа')
    completed = models.BooleanField(default=False, verbose_name='Завершён')
    success = models.BooleanField(default=False, verbose_name='Успешен')

    class Meta:
        unique_together = ['parsing', 'site_page', 'level']
        verbose_name = 'Парсинг страницы сайта'
        verbose_name_plural = 'Парсинг страниц сайтов'






