from django.contrib import admin
from ..models import Brand, BrandSite, BrandSiteMapping
from ..parsesites import parse_axop_su_brands


# @admin.register(Brand) - функционал не требуется в системе (Legacy)
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


def parse_brands(modeladmin, request, queryset):
    """ Парсить выделенные бренды
        todo в дальнейшем имеет смысл добавить поле флаг в модель BrandSiteMapping сообщающее, какие бренды парсить
    """
    # brands = queryset.values_list('site_brand__name', flat=True)
    # brands = list(brand for brand in queryset.values_list('brand__manufacturer__name', flat=True))
    brands = list(queryset.values_list('brand__manufacturer__name', flat=True))
    print(brands)
    parse_axop_su_brands(brands, max_page_number=1)
    # parse_axop_su_brands(['Roca'])


parse_brands.short_description = 'Парсить выделенные бренды'

@admin.register(BrandSiteMapping)
class BrandSiteMappingAdmin(admin.ModelAdmin):
    list_display = ('brand_name', 'site_brand',)
    list_select_related = ('brand', 'site_brand',)
    list_editable = ('site_brand',)
    search_fields = ('brand__manufacturer__name', 'site_brand__name')
    ordering = ('brand__manufacturer__name',)

    def brand_name(self, obj):
        return obj.brand.manufacturer.name
    brand_name.short_description = 'Бренд'
    brand_name.admin_order_field = 'brand__manufacturer__name'

    actions = [parse_brands, map_brands,]

    # def has_add_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False
