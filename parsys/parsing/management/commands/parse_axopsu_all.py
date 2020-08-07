from django.core.management.base import BaseCommand, CommandError
# from parsing.parsesites import ParseAxopSu


class Command(BaseCommand):
    help = 'Парсинг всего сайта axop.su'

    def handle(self, *args, **options):
        # p = ParseAxopSu()
        p = 'Пиздато!'
        self.stdout.write(self.style.SUCCESS(f'Successfully {p}'))
