from django.contrib import admin
from ..models import Parsing, File, FileData
from ..parsefiles import ParseFiles
import os


import logging
logger = logging.getLogger('debug')  # rename to do not log


def parse_files(modeladmin, request, queryset):
    """ Действие (action) - парсинг, выбранных файлов-прайсов
    """
    logger.info(f'The action "parse_files" ran with queryset: -- {queryset} --')
    pf = ParseFiles(None, modeladmin, request, queryset)
    pf.parse()


parse_files.short_description = 'Парсить выбранные файлы'


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['file', 'uploaded', 'parsing', 'parsed']
    list_display_links = None
    list_editable = ['file']
    fields = ['file', 'brand_cell', 'col_num_rows', 'col_sku', 'col_name', 'col_price', 'max_rows']

    actions = [parse_files, 'delete_selected']

    def delete_queryset(self, request, queryset):
        for file in queryset:
            print(file.file.path)
            print(file.file.path.rpartition('\\')[0])
            try:
                os.remove(file.file.path)
                os.rmdir(file.file.path.rpartition('/')[0])
                os.rmdir(file.file.path.rpartition('\\')[0])
            except:
                pass  # may be todo
        super().delete_queryset(request, queryset)


@admin.register(FileData)
class FileDataAdmin(admin.ModelAdmin):
    list_display = ['file', 'brand', 'row', 'sku', 'name', 'price', 'created']
    list_filter = ['file', 'brand']
    list_display_links = None
    search_fields = ('sku', 'name')

    actions = ['delete_selected']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
