from django.apps import AppConfig
from django.db.models.signals import pre_migrate, post_migrate


class ParsingConfig(AppConfig):
    name = 'parsing'
    verbose_name = 'Парсинг'

    def ready(self):
        from .signals import pre_migrate_copy_opencart_data, post_migrate_clear_foreignkeys
        pre_migrate.connect(pre_migrate_copy_opencart_data, sender=self)
        post_migrate.connect(post_migrate_clear_foreignkeys, sender=self)
