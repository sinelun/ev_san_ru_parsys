from django.contrib import admin
from ..models import Brand


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('manufacturer_name', 'multiplier',)
    # ordering = ('manufacturer_name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('manufacturer').order_by('manufacturer__name')

    def manufacturer_name(self, obj):
        return obj.manufacturer.name
    manufacturer_name.short_description = 'Бренд'

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

