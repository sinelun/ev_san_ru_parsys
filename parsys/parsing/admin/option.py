from django.contrib import admin
from ..models import OptionMapping, RingoProductOptionValue
from django.utils.html import format_html
from django.db.models import F, OuterRef, Subquery


@admin.register(OptionMapping)
class OptionMappingAdmin(admin.ModelAdmin):
    list_display = ('option_name', 'option_price', 'sku', 'product_name', 'product_price', 'product_price_difference',
                    # 'site_product_name', 'site_product_name','site_product_name','site_product_name',
                    'exact_match', 'checked')
    # list_select_related = ('option', 'product',)
    list_editable = ('exact_match', 'checked',)
    list_filter = ('exact_match', 'checked',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        prices = RingoProductOptionValue.objects.filter(option_value_id=OuterRef('option'))
        subquery = Subquery(prices.values('price')[:1])
        qs = qs.select_related('option', 'product', 'site_product', 'file_product') \
               .annotate(ppd=F('product__price') - subquery)

        return qs

    def option_name(self, obj):
        return obj.option.name

    option_name.short_description = 'Опция'
    option_name.admin_order_field = 'option__name'

    def product_name(self, obj):
        if not obj.product:
            return None
        name = obj.product.productdescription.name
        href = obj.product.link()
        return format_html('<a href="{}" target="_blank">{}</a>', href, name)

    product_name.short_description = 'Товар в Опенкарт'
    product_name.admin_order_field = 'product__productdescription__name'

    def option_price(self, obj):
        o = obj.option.prices.first()
        return o.price if o else None

    option_price.short_description = 'Цена'

    def product_price(self, obj):
        return obj.product.price if obj.product else None

    product_price.short_description = 'Цена'

    def product_price_difference(self, obj):
        return obj.ppd if obj.ppd is None else abs(obj.ppd)

    product_price_difference.admin_order_field = 'ppd'
    product_price_difference.short_description = 'Разность'

    def site_product_name(self, obj):
        return obj.site_product if obj.site_product else None
