from ..models import RingoProduct as Product, RingoProductDescription as ProductDescription, \
                            RingoOptionValueDescription as OptionValueDescription, \
                            FileData, \
                            OptionMapping
from difflib import SequenceMatcher
import re


def _create_object(
        option,
        sku=None,
        product=None,
        site_product=None,
        file_product=None,
        exact_match=None,
        checked=False,
):
    """ Создаёт объект сопоставления...
    """
    OptionMapping.objects.create(
        option=option,
        sku=sku,
        product=product,
        site_product=site_product,
        file_product=file_product,
        exact_match=exact_match,
        checked=checked,
    )


def _create_options_with_products(option, products):
    exact_match = True if len(products) == 1 else \
                  False if products else \
                  None
    for product in products:
        if not OptionMapping.objects.filter(option=option, product=product):
            _create_object(
                option,
                product.model,
                product,
                None,
                None,
                exact_match,
                False,
            )


def _exact_match_option_name_product():
    """ Ищет полные совпадения имен опции (OptionValueDescription.name) и товара (Product.model).
    """
    for option in OptionValueDescription.objects.exclude(matchings__checked=True):
        products = Product.objects.filter(productdescription__name__iexact=option.name)
        _create_options_with_products(option, products)


def _exact_match_option_sku_product():
    """ Ищет совпадения последовательности символов в имени опции (OptionValueDescription.name)
        c артикулом товара (Product.model).
    """
    for option in OptionValueDescription.objects.exclude(matchings__checked=True):
        maybe_sku = re.findall(r'[0-9A-Z-.]{5,}', option.name)
        products = []
        for sku in maybe_sku:
            products += Product.objects.filter(model__iexact=sku)
        _create_options_with_products(option, products)


def _match_option_name_product():
    """ Ищет неполные совпадения имен опции (OptionValueDescription.name) и товара (Product.model)
        среди опций с exact_match != True
    """
    i=0; j=0
    for option in OptionValueDescription.objects.exclude(matchings__exact_match=True):
        option_name = option.name.lower()
        words = re.findall(r'\w{4,}', option.name)
        i += 1
        # print(i, words)
        products = []
        for word in words:
            product_ids = [product.pk for product in products]
            products += Product.objects.exclude(pk__in=product_ids).filter(productdescription__name__icontains=word)
            # print('products = ', products)
        max_ratio = 0.75
        match_product = None
        for product in products:
            # product_name = (product.model + ' ' + product.productdescription.name).lower()
            product_name = (product.productdescription.name).lower()
            sm = SequenceMatcher(None, option_name, product_name)
            r = sm.ratio()
            if r > max_ratio:
                max_ratio = r
                match_product = product
        if match_product:
            product = match_product
            j += 1
            print(j, max_ratio, option_name, product.productdescription.name, sep=' | ')
            if not OptionMapping.objects.filter(option=option, product=product):
                _create_object(
                    option,
                    product.model,
                    product,
                    None,
                    None,
                    False,
                    False,
                )


def _exact_match_option_sku_file():
    """ Ищет совпадения последовательности символов в имени опции (OptionValueDescription.name)
        c артикулом товара в данных прайсов (Product.model).
    """
    i=0; j=0
    for option in OptionValueDescription.objects.exclude(matchings__exact_match=True):
        maybe_sku = re.findall(r'[0-9A-Z-.]{5,}', option.name)
        i+=1
        print(i, maybe_sku)
        products = []
        for sku in maybe_sku:
            products += FileData.objects.filter(sku__iexact=sku)
            j+=1
            print(j, products)
        # _create_options_with_products(option, products)


def _exact_match_option_name_file():
    """ Ищет совпадения последовательности символов в имени опции (OptionValueDescription.name)
        c артикулом товара в данных прайсов (Product.model).
    """
    i=0
    for option in OptionValueDescription.objects.exclude(matchings__exact_match=True):
        products = FileData.objects.filter(name__iexact=option.name)
        # _create_options_with_products(option, products)
        if products:
            i+=1
            print(i, products)

# todo
def match_option_name_product(options=[]):
    """
    :param options:
    :return: nothing
    """
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
    # _exact_match_option_name_product()
    # _exact_match_option_sku_product()
    # _match_option_name_product()
    # _exact_match_option_sku_file()
    _exact_match_option_name_file()

    # match_option_name_product(res)

    # i=0
    # for product in Product.items.active().all():
    #     i+=1
    #     print(i, product, product.status)
