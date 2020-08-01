from ..models import RingoProduct as Product, RingoProductDescription as ProductDescription, \
                            RingoOptionValueDescription as OptionValueDescription, OptionMapping
from difflib import SequenceMatcher
import re


def match_option_sku_product():
    """ Ищет совпадения последовательности символов в имени опции (OptionValueDescription.name)
        c артикулом товара (Product.model).
        Возвращает список объектов опций, у которых совпадения по артикулу нет.
    """
    i = 0
    result = []
    for option in OptionValueDescription.objects.all():
        maybe_sku = re.findall(r'[0-9A-Z-.]{5,}', option.name)
        # print(i, maybe_sku, option.name)
        products = []
        for sku in maybe_sku:
            products += Product.objects.filter(model__iexact=sku)
        if products:
            i += 1
            print(i, maybe_sku, option.name)
            print(products)
        else:
            result.append(option)
    return result


def match_option_name_product(options=[]):
    i = 0; j = 0
    for option in options if options else OptionValueDescription.objects.all():
        i += 1
        print(i, option.name)
        option_name = option.name.lower()
        max_ratio = 0
        match_product = None
        for product in ProductDescription.objects.select_related('product_id').all():
            product_name = (product.product_id.model + ' ' + product.name).lower()
            sm = SequenceMatcher(None, option_name, product_name)
            r = sm.ratio()
            if r > max_ratio:
                max_ratio = r
                if max_ratio > 0.85:
                    match_product = product
        if match_product:
            j += 1
            print(j, max_ratio, product_name)


def match_option_product():
    res = match_option_sku_product()
    # match_option_name_product(res)

    # i=0
    # for product in Product.items.active().all():
    #     i+=1
    #     print(i, product, product.status)
