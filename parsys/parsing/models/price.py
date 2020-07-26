from django.db import models
from .opencart import RingoProduct as Product, RingoOptionValueDescription as Option
from .parsing import Parsing
from .product import SiteProductPage


class SitePriceParsing(models.Model):
    """ Цены на товары на сайтах-донорах.
    """
    parsing = models.ForeignKey(Parsing, on_delete=models.CASCADE, verbose_name='Парсинг')
    product = models.ForeignKey(SiteProductPage, on_delete=models.CASCADE, related_name='prices', verbose_name='Товар')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    price_discount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена без скидки')

    class Meta:
        unique_together = ['parsing', 'product']
        verbose_name = 'Цена на сайте'
        verbose_name_plural = 'Цены на сайте'


class PriceChangeSession(models.Model):
    """ Сессии изменения цен.
    """
    created = models.DateTimeField(auto_now_add=True, verbose_name='Произведено')

    def __str__(self):
        return self.created


class ProductPriceHistory(models.Model):
    """ История изменения цен на товары.
    """
    change_session = models.ForeignKey(PriceChangeSession, on_delete=models.CASCADE, verbose_name='Дата')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, verbose_name='Товар в опенкарт',
                                null=True, blank=True, default=None)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')

    class Meta:
        verbose_name = 'История изменения цен на товары'
        verbose_name_plural = 'История изменения цен на товары'


class OptionPriceHistory(models.Model):
    """ История изменения цен опций.
    """
    change_session = models.ForeignKey(PriceChangeSession, on_delete=models.CASCADE, verbose_name='Дата')
    option = models.ForeignKey(Option, on_delete=models.SET_NULL, verbose_name='Опция в опенкарт',
                                null=True, blank=True, default=None)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')

    class Meta:
        verbose_name = 'История изменения цен опций'
        verbose_name_plural = 'История изменения цен опций'
