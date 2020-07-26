from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.sessions.models import Session
from parsing.data_transfer import copy_data_from_opencart, clear_foreignkeys


@receiver(post_save, sender=Session)
def copy_opencart_data(sender, instance, **kwargs):
    if kwargs['created']:
        print('Копируются таблицы Опенкарта после старта сессии...')
        copy_data_from_opencart()
        print('Очищаются таблицы от отсутствующих внешних ключей после миграции...')
        clear_foreignkeys()


def pre_migrate_copy_opencart_data(sender, **kwargs):
    print('Копируются таблицы Опенкарта перед стартом миграции...')
    copy_data_from_opencart()


def post_migrate_clear_foreignkeys(sender, **kwargs):
    print('Очищаются таблицы от отсутствующих внешних ключей после миграции...')
    clear_foreignkeys()




