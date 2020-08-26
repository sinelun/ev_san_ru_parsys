from django.core.management.base import BaseCommand, CommandError
from ...continue_parsing import continue_parsing
# from parsing.parsesites import ParseAxopSu


class Command(BaseCommand):
    help = 'Продолжение последнего незаконченного парсинга, начатого не позднее одного дня назад'

    def handle(self, *args, **options):
        continue_parsing()
