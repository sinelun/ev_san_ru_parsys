from django.db import models


class Parsing(models.Model):
    TYPE_CHOICES = (
        ('files', 'файлы'),  # парсинг файлов
        ('sites', 'сайты'),  # парсинг сайтов целиком
        ('products', 'продукты'),  # парсинг страниц с продуктами
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=None, null=True, blank=True, verbose_name='Тип')
    start = models.DateTimeField(auto_now_add=True, verbose_name='Начало')
    finish = models.DateTimeField(auto_now=True, verbose_name='Конец')
    completed = models.BooleanField(default=False, verbose_name='Завершён')

    @property
    def duration(self):
        return self.finish - self.start
    duration.fget.short_description = 'Продолжительность'

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = 'Парсинг'
        verbose_name_plural = 'Парсинги'
        ordering = ['-finish']


