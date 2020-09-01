from django.db import models


class UserSettingSection(models.Model):
    name = models.CharField(max_length=60, unique=True, verbose_name='Название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Раздел настроек'
        verbose_name_plural = 'Разделы настроек'
        ordering = ['name']


class UserSetting(models.Model):
    TYPE_CHOICES = (
        ('str', 'строка'),
        ('int', 'целое число'),
        ('dec', 'число с точкой'),
    )
    section = models.ForeignKey(UserSettingSection, on_delete=models.CASCADE,
                                related_name='settings', verbose_name='Раздел')
    name = models.CharField(max_length=60, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, default='', verbose_name='Описание')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='str', blank=True, verbose_name='Тип значения')
    value = models.CharField(max_length=256, blank=True, default='', verbose_name='Значение')

    def save(self,  *args, **kwargs):
        if self.type == 'int':
            try:
                self.value = int(self.value)
            except:
                self.value = 0
        elif self.type == 'dec':
            try:
                self.value = float(self.value.replace(',', '.'))
            except:
                self.value = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Настройка'
        verbose_name_plural = 'Настройки'
        ordering = ['section', 'name']
