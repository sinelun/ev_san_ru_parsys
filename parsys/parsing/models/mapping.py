from django.db import models
from .opencart import RingoProduct as Product, RingoOptionValueDescription as Option
from .product import SiteProductPage, FileProduct
from .brand import Brand, BrandSite


class MappingAbstract(models.Model):
    """ Поля характерные для сопоставлений:
        exact_match = True - не дублирующееся полное совпадение по артикулу
        checked - выставляется в True вручную при проверке,
        тогда exact_match не играет роли
    """
    exact_match = models.BooleanField(null=True, blank=True, default=None, verbose_name='Однозначно')
    checked = models.BooleanField(default=False, verbose_name='Проверено')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Добавлено')
    updated = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        abstract = True


class BrandSiteMapping(models.Model):
    """ Сопоставление брендов
    """
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name='Бренд')
    site_brand = models.ForeignKey(BrandSite,
                                   on_delete=models.SET_NULL, null=True, blank=True, default=None,
                                   verbose_name='Бренд на сайте')

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        ordering = ['brand']


class SiteProductMapping(MappingAbstract):
    """ Сопоставление товаров опенкарта с товарами сайтов-доноров.
    """
    product = models.OneToOneField(Product, on_delete=models.CASCADE, verbose_name='Товар в опенкарт')
    site_product_page = models.ForeignKey(SiteProductPage,
                                          on_delete=models.SET_NULL, blank=True, null=True, default=None,
                                          verbose_name='Страница товара на сайте')

    class Meta:
        unique_together = ['product', 'site_product_page']
        verbose_name = 'Cопоставление товара с сайтом'
        verbose_name_plural = 'Cопоставление товаров с сайтами'


class FileProductMapping(MappingAbstract):
    """ Сопоставление товаров опенкарта с прайсами.
    """
    product = models.OneToOneField(Product, on_delete=models.CASCADE, verbose_name='Товар в опенкарт')
    file_product = models.ForeignKey(FileProduct, on_delete=models.SET_NULL, blank=True, null=True, default=None,
                                     verbose_name='Товар в прайсе ')

    class Meta:
        unique_together = ['product_id', 'file_product']
        verbose_name = 'Cопоставление товара с прайсом'
        verbose_name_plural = 'Cопоставление товаров с прайсами'


class OptionMapping(MappingAbstract):
    """ Модель сопоставления опций Опенкарта с:
        1) товарами Опенкарта (RingoProduct);
        2) с товарами с сайтов доноров (SiteProductPage);
        3) с товарами из файлов-прайсов (FileProduct)
        Артикул (sku) заполняется при выполнении скрипта сопоставления предполагаемыми значениями,
        точные значения выставляются вручную.
        Выставление артикула - результат операции сопоставления, так как в дальнейшем опция будет связана именно с
        артикулом, а не с другими полями, которые здесь нужны лишь для справочной информации во время ручной обработки.
        Нет необходимости в сопоставлении опций со всеми тремя моделями,
        но достаточно сопоставление только с одной, но в строгой последовательности: 1), 2), 3) (см. выше)
    """
    option = models.ForeignKey(Option, null=True, blank=True, default=None, related_name='matchings',
                               on_delete=models.CASCADE, verbose_name='Опция')
    sku = models.CharField(max_length=60, null=True, blank=True, default=None, verbose_name='Артикул')
    product = models.ForeignKey(Product, null=True, blank=True, default=None,
                                on_delete=models.SET_NULL, verbose_name='Товар в Опенкарт')
    site_product = models.ForeignKey(SiteProductPage, null=True, blank=True, default=None,
                                on_delete=models.SET_NULL, verbose_name='Товар на сайте-доноре')
    file_product = models.ForeignKey(FileProduct, null=True, blank=True, default=None,
                                     on_delete=models.SET_NULL, verbose_name='Товар в прайсе')

    class Meta:
        verbose_name = 'Опция - товар'
        verbose_name_plural = 'Опции - товары'

