from django.contrib import admin
from ..models import Site,SiteProductPage
from django.contrib import messages


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['url', 'created', 'updated']
    list_display_links = None
    fields = []

    actions = ['delete_selected']

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