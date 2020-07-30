from django.contrib import admin
from ..models import Brand, BrandSite, BrandSiteMapping


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('manufacturer_name', 'multiplier',)
    list_select_related = ('manufacturer',)
    list_editable = ('multiplier',)
    search_fields = ('manufacturer__name',)
    ordering = ('manufacturer__name',)
    readonly_fields = ('manufacturer',)

    def manufacturer_name(self, obj):
        return obj.manufacturer.name
    manufacturer_name.short_description = 'Бренд'
    manufacturer_name.admin_order_field = 'manufacturer__name'

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


def map_brands(modeladmin, request, queryset):
    """ Сопоставление брендов.
    """
    for obj in queryset:
        site_brand = BrandSite.objects.filter(name__iexact=obj.brand.manufacturer.name).first()
        print(obj.brand.manufacturer.name, site_brand)
        obj.site_brand = site_brand
        obj.save()


map_brands.short_description = 'Сопоставить выделенные бренды'


@admin.register(BrandSiteMapping)
class BrandSiteMappingAdmin(admin.ModelAdmin):
    list_display = ('brand_name', 'site_brand',)
    list_select_related = ('brand', 'site_brand',)
    list_editable = ('site_brand',)
    search_fields = ('brand__manufacturer__name', 'site_brand__name')

    def brand_name(self, obj):
        return obj.brand.manufacturer.name
    brand_name.short_description = 'Бренд'
    brand_name.admin_order_field = 'brand__manufacturer__name'

    actions = [map_brands]

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False
