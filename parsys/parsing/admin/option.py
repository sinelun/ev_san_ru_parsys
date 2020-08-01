from django.contrib import admin
from ..models import OptionMapping


@admin.register(OptionMapping)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('option', )
    # list_select_related = ('manufacturer',)
    # list_editable = ('multiplier',)
    # search_fields = ('manufacturer__name',)
    # ordering = ('manufacturer__name',)
    # readonly_fields = ('manufacturer',)
    #
    # def manufacturer_name(self, obj):
    #     return obj.manufacturer.name
    # manufacturer_name.short_description = 'Бренд'
    # manufacturer_name.admin_order_field = 'manufacturer__name'
    #
    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False
