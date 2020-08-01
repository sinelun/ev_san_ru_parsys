from opencart.models import RingoProduct as Product, \
                            RingoManufacturer as Manufacturer, \
                            RingoProductDescription as ProductDescription
from parsing.models import SiteProductPage, SiteProductMapping, BrandSiteMapping
from difflib import SequenceMatcher


def match_site_product_exact():
    """ Точное совпадение с артикулом """
    i = 0
    for product in Product.objects.all():
        # точное совпадение артикулов
        matches = SiteProductPage.objects.filter(sku__iexact=product.model.strip())
        # matches = SiteProductPage.objects.filter(sku__iexact=product.sku.strip())
        if matches:
            i += 1; print(i, matches)
            # если совпадение только одно, отметим это как True для дальнейшего сопоставления по названиям
            exact_match = len(matches) == 1
            for page in matches:
                print(page)
                SiteProductMapping.objects.update_or_create(
                    product_id=product.product_id,
                    site_product_page=page,
                    defaults={'exact_match': exact_match}
                )
        else:
            # print(product)
            SiteProductMapping.objects.update_or_create(product_id=product.product_id,
                                                        defaults={'site_product_page': None, 'exact_match': None})


def match_site_product_diff():
    """ Совпадение близкое по названию в соответствующих брендах """
    i = 0
    for product in SiteProductMapping.objects.filter(site_product_page=None):
        try:
            opencart_product = Product.objects.get(pk=product.product_id)
            opencart_brand = opencart_product.manufacturer_id.pk
            opencart_name = opencart_product.ringoproductdescription.name.lower()
            # Бренд на сайте todo для нескольких сайтов
            bsm = BrandSiteMapping.objects.get(brand_id=opencart_brand)  # todo Здесь не помешает отдельный try... except на случай, если BrandSiteMapping не заполнен или не обновлён
            brand = bsm.site_brand.strip().lower()
            if not brand:
                continue
            # print(i, f'brand: «{brand}» | ', opencart_brand, opencart_name)
            max_ratio = 0
            match_product_page = None
            for prod in SiteProductPage.objects.filter(brand__iexact=brand):
                site_product_name = prod.name.lower()
                sm = SequenceMatcher(None, opencart_name, site_product_name)
                # print('--', opencart_name, site_product_name, sep=' | ')
                r = sm.ratio()
                # print('---', r)
                if r > max_ratio:
                    max_ratio = r
                    if max_ratio > 0.65:
                        match_product_page = prod
            if match_product_page:
                i += 1
                print(i, max_ratio,
                      f'{opencart_product.manufacturer_id.name} {opencart_product.model}',
                      f'{match_product_page.brand} {match_product_page.sku}',
                      sep=' | '
                      )
                print(opencart_name, match_product_page.name, sep=' | ')
        except:
            # raise Exception
            continue


def match_site_product():
    """ Сопоставляет все товары «Опенкарта» (Product), со страницами сайтов (SiteProductPage) """
    match_site_product_exact()
    # match_site_product_diff()