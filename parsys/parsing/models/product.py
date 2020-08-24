from django.db import models
from .parsing import Parsing
from .site import SitePage
from .file import File


class ProductAbstract(models.Model):
    """ Поля характеризующие товар, как в прайсах, так и на сайтах
    """

    brand = models.CharField(max_length=60, verbose_name='Бренд')
    sku = models.CharField(max_length=60, verbose_name='Артикул')
    name = models.CharField(max_length=250, verbose_name='Товар')

    def __str__(self):
        return f'({self.sku}) {self.name}'

    class Meta:
        abstract = True


class SiteProductPage(ProductAbstract):
    """ Страница товара на сайте-доноре. Дополняет SitePage данными товра ProductAbstract.
        Как и SitePage создаётся один раз. По этой модели идёт споставление товаров
        с базой данных Opencart (SiteProductMapping).
    """

    site_page = models.OneToOneField(SitePage, on_delete=models.CASCADE,
                                     related_name='product_data', verbose_name='Страница сайта')
    site_code = models.CharField(max_length=64, verbose_name='Код на сайте')

    class Meta:
        verbose_name = 'Cтраница товара на сайте'
        verbose_name_plural = 'Cтраницы товаров на сайтах'


class FileData(ProductAbstract):
    """ Данные из файлов с прайсами.
        Удаляются при удалении соответствующих парсинга и файла, откуда они взяты.
        Это также приведёт к установке actual_data в NULL в модели FileProduct.
    """

    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='data', verbose_name='Файл')
    sheet = models.CharField(max_length=60, verbose_name='Лист')
    row = models.PositiveIntegerField(blank=True, null=True, default=None, verbose_name='Строка')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Цена')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создана')

    class Meta:
        verbose_name = 'Данные прайсов'
        verbose_name_plural = 'Данные прайсов'
        ordering = ['file', 'brand', 'sheet', 'row']


class FileProduct(models.Model):
    """ Товар в файлах-прайсах. Уникальный ключ - артикул товара.
        Записи создаются один раз при парсинге файлов-прайсов, затем обновляются.
        Модель нужна для сопоставления товаров и опций с прайсами.
        actual_data будет NULL, если будут удалены соответствующие данные парсингов
        через удаление самих парсингов или файлов.
    """
    sku = models.CharField(max_length=60, unique=True, verbose_name='Артикул')
    actual_data = models.ForeignKey(FileData, on_delete=models.SET_NULL, null=True, blank=True, default=None,
                                    verbose_name='Актуальные данные прайса')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated = models.DateTimeField(auto_now=True, verbose_name='Обновлён')

    def __str__(self):
        return self.sku

    class Meta:
        verbose_name = 'Товар в прайсе'
        verbose_name_plural = 'Товары в прайсах'

