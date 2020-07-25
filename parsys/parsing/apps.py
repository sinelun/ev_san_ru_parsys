from django.apps import AppConfig
from django.db.models.signals import pre_migrate, post_migrate


class ParsingConfig(AppConfig):
    name = 'parsing'
    verbose_name = 'Парсинг'

    # def ready(self):
    #     import parsing.signals as signals
    #     pre_migrate.connect(signals.pre_migrate_copy_opencart_data, sender=self)
    #     post_migrate.connect(signals.post_migrate_clear_foreignkeys, sender=self)
