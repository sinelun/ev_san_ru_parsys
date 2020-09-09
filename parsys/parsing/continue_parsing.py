from .models import Parsing
from datetime import datetime, timedelta
from django.utils import timezone
from .parsefiles import ParseFiles
from .parsesites import parse_axop_su_site

import os

import logging
logger = logging.getLogger('debug')  # do not log


def continue_parsing():
    """ Продолжение незаконченного парсинга.
        Используется для cron задач.
    """

    # Если парсинг уже запущен, значит есть папка-флаг, и новый парсинг запущен не будет, а в конце она удаляется
    try:
        flag_dir = os.path.dirname(__file__) + '/_tmp_flag_dir_continue_parsing'
        os.mkdir(flag_dir)
    except:
        return

    try:

        # Последний незаконченный парсинг не старше одного дня
        last_day = datetime.now(tz=timezone.utc) - timedelta(days=1)
        last_parsing = Parsing.objects.filter(completed=False, start__gt=last_day).latest('start')

        if last_parsing:

            logger.info(f'==========================================================================')
            logger.info(f'Есть незаконченный парсинг -- {last_parsing} -- типа -- {last_parsing.type} -- '
                        f'за последний день -- {last_day} --')

            if last_parsing.type == 'files':
                logger.info(f'Возобновлён последний незаконченный парсинг файлов -- {last_parsing} --')
                pf = ParseFiles(last_parsing)
                pf.parse()
            elif last_parsing.type == 'sites':
                logger.info(f'Возобновлён последний незаконченный парсинг сайтов -- {last_parsing} --')
                parse_axop_su_site()
            elif last_parsing.type == 'products':
                logger.info(f'Возобновлён последний незаконченный парсинг товаров -- {last_parsing} --')
            else:
                logger.error(f'Неизвестный тип парсинга -- {last_parsing.type} --')
                raise Exception('Неизвестный тип парсинга!')

    except:
        logger.error(f'There was appeared some error during the continuing of the parsing.')
    finally:
       os.rmdir(flag_dir)


