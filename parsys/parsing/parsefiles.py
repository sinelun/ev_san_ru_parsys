from .models import Parsing, File, FileData
from openpyxl import load_workbook
from django.contrib import messages


class ParseFiles:
    def __init__(self, parsing=None, modeladmin=None, request=None, queryset=None):

        self.pasing = parsing
        if not self.parsing:
            self.parsing = Parsing(type='files')
            self.parsing.save()

        # Если парсинг завершён, ничего не делать
        self.do_nothing = self.parsing.completed

        if not self.do_nothing:
            # Файлы для парсинга
            self.queryset = queryset if queryset else File.objects.filter(parsing=self.parsing)

            # Для сообщений в админ. панели
            self.modeladmin = modeladmin
            self.request = request

    def parse(self, parsing=None, modeladmin=None, request=None, queryset=None):
        self.__init__(self, parsing=None, modeladmin=None, request=None, queryset=None)
        if self.do_nothing:
            return
        for file in self.queryset:
            if file.parsed:
                self._admin_message(f'Файл {file} уже был обработан ранее.', 'WARNING')
                continue
            try:
                wb = load_workbook(file.file.path, read_only=True)
            except:
                self._admin_message(f'Невозможно прочитать файл {file}', 'ERROR')
                continue
            for ws in wb:
                print(ws)


    def _admin_message(self, message, level):
        if not self.modeladmin or not self.request:
            return
        self.modeladmin.message_user(self.request, message, exec(f'messages.{level}'))
