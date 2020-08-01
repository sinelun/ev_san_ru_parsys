from opencart.models import RingoProduct as Product, \
                            RingoManufacturer as Manufacturer, \
                            RingoProductDescription as ProductDescription
from parsing.models import FileData, SiteProductPage
# from difflib import SequenceMatcher


def match_file_product_exact():
    """ Точное совпадение с артикулом """
    i = 0
    for product in Product.objects.all():
        # точное совпадение артикулов
        matches = FileData.objects.filter(sku__iexact=product.model.strip())
        if matches:
            if not SiteProductPage.objects.filter(sku__iexact=product.model.strip()):
                i += 1; print(i, matches)
            # если совпадение только одно, отметим это как True для дальнейшего сопоставления по названиям
            # exact_match = len(matches) == 1
            # for raw in matches:
            #     print(raw)
        else:
            pass


def match_file_product():
    """ Сопоставляет все товары «Опенкарта» (Product), с прайсами """
    match_file_product_exact()


