from .models import Parsing
from datetime import datetime, timedelta
from django.utils import timezone
from .parsefiles import ParseFiles

import logging
logger = logging.getLogger('debug')  # do not log


def continue_parsing():
    """ Продолжение незаконченного парсинга.
        Используется для cron задач.
    """

    # Последний незаконченный парсинг не старше одного дня
    last_day = datetime.now(tz=timezone.utc) - timedelta(days=1)
    last_parsing = Parsing.objects.filter(completed=False, start__gt=last_day).latest('start')
    logger.info(f'==========================================================================')
    logger.info(f'The last unfinished parsing -- {last_parsing} -- last day -- {last_day} --')
    if last_parsing:
        if last_parsing.type == 'files':
            logger.info(f'Continue the last unfinished file parsing -- {last_parsing} --')
            # Возобновляем последний незаконченный парсинг файлов
            pf = ParseFiles(last_parsing)
            pf.parse()
        elif last_parsing.type == 'sites':
            logger.info('Continue the last unfinished site parsing')
        elif last_parsing.type == 'products':
            logger.info('Continue the last unfinished product parsing')
        else:
            raise Exception('Неизвестный тип парсинга!')


