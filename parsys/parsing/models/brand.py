from django.db import models
from .opencart import RingoManufacturer as Manufacturer
from .site import Site


class Brand(models.Model):
    """ Все бренды Опенкарта, а также коэффициенты наценок для них.
        Модель-обёртка для RingoManufacturer, постоянно перезаписываемой из Опенкарта.
        Данные этой модели не перезаписываются, а обновляются.
    """
    manufacturer = models.OneToOneField(Manufacturer, on_delete=models.SET_NULL, null=True, blank=True, default=None,
                                           verbose_name='Бренд')
    multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1, verbose_name='Коэффициент цен')

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'


class BrandSite(models.Model):
    """ Все бренды на сайтах-донорах.
        Модель заполняется данными при первом парсинге сайта-донора, затем обновляется.
        Записи удаляются при удалении сайта.
    """
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name='Сайт')
    name = models.CharField(max_length=60, unique=True, verbose_name='Бренд')
    url = models.URLField(unique=True, verbose_name='URL страницы бренда')
    actual = models.BooleanField(default=True, verbose_name='Присутствует на сайте')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Добавлен')
    updated = models.DateTimeField(auto_now=True, verbose_name='Обновлён')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Бренд на сайте'
        verbose_name_plural = 'Бренды на сайтах'
        ordering = ['site', 'name']
