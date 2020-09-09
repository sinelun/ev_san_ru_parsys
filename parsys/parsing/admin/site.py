from django.contrib import admin
from ..models import Site, SiteProductPage
from ..parsesites import parse_axop_su_site
from django.contrib import messages


import logging
logger = logging.getLogger(__name__)


def parse_site(modeladmin, request, queryset):
    """ Действие (action) - парсинг сайта
    """
    logger.info(f'Запущено действие (action) из админки parse_site()')
    parse_axop_su_site()


parse_site.short_description = 'Парсить выбранный сайт'


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['url', 'created', 'updated']
    list_display_links = None
    fields = []

    actions = [parse_site, 'delete_selected']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SiteProductPage)
class SiteProductPage(admin.ModelAdmin):
    list_display = ['site_page', 'brand', 'sku', 'site_code', 'name']
    list_select_related = ['site_page']
    ordering = ['brand', 'name']
    list_display_links = None
    search_fields = ['sku', 'name', 'site_code']
    list_filter = ['brand']
    list_per_page = 25

    actions = ['delete_selected']

    def has_add_permission(self, request, obj=None):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     return False

    def has_change_permission(self, request, obj=None):
        return False

    # actions = [map_data, 'delete_selected']