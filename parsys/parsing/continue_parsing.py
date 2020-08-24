from .models import Parsing
from datetime import datetime, timedelta
from django.utils import timezone


def continue_parsing():
    """ Продолжение незаконченного парсинга.
        Используется для cron задач.
    """

    # Последний незаконченный парсинг не старше одного дня
    last_day = datetime.now(tz=timezone.utc) - timedelta(days=1)
    last_parsing = Parsing.objects.filter(completed=False, start__gt=last_day).last()
    if last_parsing:
        if last_parsing.type == 'files':
            pass
        elif last_parsing.type == 'sites':
            pass
        elif last_parsing.type == 'products':
            pass
        else:
            raise Exception('Неизвестный тип парсинга!')


