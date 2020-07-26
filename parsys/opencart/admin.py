from django.contrib import admin
from .models import RingoManufacturer, RingoProduct, RingoProductDescription, RingoProductOptionValue


@admin.register(RingoProduct)
class RingoProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'manufacturer_id', 'model', 'get_name', 'price')
    list_filter = ('manufacturer_id',)
    list_per_page = 50
    ordering = ('manufacturer_id', 'productdescription__name')
    search_fields = ('model', 'productdescription__name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('manufacturer_id', 'productdescription')

    def get_name(self, obj):
        return obj.productdescription.name

    get_name.admin_order_field = 'productdescription__name'
    get_name.short_description = 'Наименование'

    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + \
               [field.name for field in obj._meta.fields] + \
               [field.name for field in obj._meta.many_to_many]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# todo @admin.register(RingoProductOptionValue)
# class RingoProductOptionValueAdmin(admin.ModelAdmin):
#     list_display = ('option_value_id', 'product_id', 'price')
#
#     readonly_fields = []
#
#     def get_readonly_fields(self, request, obj=None):
#         return list(self.readonly_fields) + \
#                [field.name for field in obj._meta.fields] + \
#                [field.name for field in obj._meta.many_to_many]
#
#     def has_add_permission(self, request, obj=None):
#         return False
#
#     def has_delete_permission(self, request, obj=None):
#         return False
#
#     def has_change_permission(self, request, obj=None):
#         return False