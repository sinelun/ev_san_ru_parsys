from django.db import models
from .parsing import Parsing
from ..validators import validate_file_extension


class File(models.Model):
    """Файлы с прайсами в формате xlsx"""

    file = models.FileField(upload_to='prices/%Y/%m/%d', validators=[validate_file_extension],
                            verbose_name="Файл в формате xlsx")
    max_rows = models.SmallIntegerField(default=1000, verbose_name='Максимум строк на листе')
    brand_cell = models.CharField(max_length=10, default='2/1', verbose_name='Адрес ячейки с брендом (строка/колонка)')
    col_num_rows = models.SmallIntegerField(default=1, verbose_name='Колонка с номерами строк')
    col_sku = models.SmallIntegerField(default=2, verbose_name='Колонка с артикулами')
    col_name = models.SmallIntegerField(default=3, verbose_name='Колонка с названием товара')
    col_price = models.SmallIntegerField(default=5, verbose_name='Колонка с ценой товара')
    uploaded = models.DateTimeField(auto_now=True, verbose_name='Загружен')
    parsing = models.ForeignKey(Parsing, on_delete=models.CASCADE, default=None, blank=True, null=True,
                                    related_name='files', verbose_name='Парсинг')
    last_parsed_sheet = models.IntegerField(default=0, verbose_name='Последний обработанный лист')
    parsed = models.BooleanField(default=False, verbose_name='Обработан')

    def __str__(self):
        return self.file.name

    class Meta:
        verbose_name = 'Файл с прайсом'
        verbose_name_plural = 'Файлы с прайсами'
        ordering = ['-uploaded']

