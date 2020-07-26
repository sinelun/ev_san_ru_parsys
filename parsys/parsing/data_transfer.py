""" Перенос таблиц с данными из «Опенкарт» и обратно
"""

from django.db import connection
from django.conf import settings
from parsing.models import \
    Brand, FileProductMapping, OptionMapping, OptionPriceHistory, ProductPriceHistory, SiteProductMapping, \
    RingoManufacturer, RingoProduct, RingoOptionValueDescription
import time


def copy_data_from_opencart():
    """ Оперативно копирует нужные таблицы из БД Опенкарта в БД Парсинга.
        --
        !!! Не будет работать, если в Opencart установлено более одного язвка,
        что связано с таблицами ..._description, где PRIMARY KEY cоставной:
        PRIMARY KEY (`option_value_id`, `language_id`), например.
        На момент разработки нет смысла в реализации функционала для поддержки такого ключа.
    """

    with connection.cursor() as cursor:
        scheme1 = settings.DATABASES['default']['NAME']
        scheme2 = settings.DATABASES['opencart']['NAME']

        tables = (
            ('ringo_manufacturer', 'manufacturer_id'),
            ('ringo_product', 'product_id'),
            ('ringo_product_description', 'product_id'),
            ('ringo_option_value_description', 'option_value_id'),
            ('ringo_product_option_value', 'product_option_value_id'),
        )

        for table in tables:
            start = time.time()
            table_name = table[0]
            primary_key = table[1]
            cursor.execute(f"""
                SELECT * FROM information_schema.tables 
                WHERE `TABLE_SCHEMA` = '{scheme1}' AND TABLE_NAME = '{table_name}';
            """)
            table_exists = cursor.fetchone()
            if table_exists:
                cursor.execute(f"""
                    SET FOREIGN_KEY_CHECKS = 0;                        
                    TRUNCATE TABLE {scheme1}.{table_name};
                    SET FOREIGN_KEY_CHECKS = 1;
                    INSERT INTO {scheme1}.{table_name} SELECT * FROM {scheme2}.{table_name};
                """)
            else:
                cursor.execute(f"""                        
                    CREATE TABLE {scheme1}.{table_name} AS SELECT * FROM {scheme2}.{table_name};
                    ALTER TABLE {scheme1}.{table_name} ADD PRIMARY KEY (`{primary_key}`);
                """)
            end = time.time()

            print('Скопирована таблица', table_name, f'за {end - start} с.')


def clear_foreignkeys():
    """ Очищает таблицы от записей, не соответствующие внешнним ключам, после миграции.
    """
    Brand.objects.exclude(manufacturer__in=RingoManufacturer.objects.all()).delete()
    FileProductMapping.objects.exclude(product__in=RingoProduct.objects.all()).delete()
    SiteProductMapping.objects.exclude(product__in=RingoProduct.objects.all()).delete()
    OptionMapping.objects.exclude(product__in=RingoProduct.objects.all()).delete()
    OptionMapping.objects.exclude(option__in=RingoOptionValueDescription.objects.all()).delete()
    ProductPriceHistory.objects.exclude(product__in=RingoProduct.objects.all()).delete()
    OptionPriceHistory.objects.exclude(option__in=RingoOptionValueDescription.objects.all()).delete()


# --- Вспомогательные функции ---


def run_copy_data_between_tables(tables: tuple):
    """ Вспомогательная функция для быстрого переноса данных таблиц, без проверки на существование последних.
        tables - кортеж вида ((scheme1.table1_name, scheme2.table1_name), (scheme1.table2_name, scheme2.table2_name),)
    """
    with connection.cursor() as cursor:
        for table in tables:
            from_table = table[0]
            to_table = table[1]
            query = f"""
                        SET FOREIGN_KEY_CHECKS = 0;                        
                        TRUNCATE TABLE {to_table};
                        SET FOREIGN_KEY_CHECKS = 1;
                        INSERT INTO {to_table} SELECT * FROM {from_table};
                    """
            start = time.time()
            cursor.execute(query)
            end = time.time()
            print(f'Скопированы данные из {from_table} в {to_table} за {end - start} с.')


def copy_data_between_tables_4():
    print('Копиарование таблиц из локальной базы evsan_parsing4 в текущую')

    query = f"""
                SET FOREIGN_KEY_CHECKS = 0;
                                   
                TRUNCATE TABLE evsan_parsing42.parsing_brand;
                INSERT INTO evsan_parsing42.parsing_brand (`id`, `manufacturer_id`, `multiplier`)
                SELECT `id`, `manufacturer_id`, `multiplier` FROM evsan_parsing4.parsing_brand;

                TRUNCATE TABLE evsan_parsing42.parsing_brandsite;
                INSERT INTO evsan_parsing42.parsing_brandsite 
                (`id`, `name`, `url`, `actual`, `created`, `updated`, `site_id`)
                SELECT `id`, `name`, `url`, 
                (SELECT 1), 
                (SELECT `updated` FROM evsan_parsing4.parsing_site WHERE id=1),
                (SELECT `updated` FROM evsan_parsing4.parsing_site WHERE id=1),
                site_id
                FROM evsan_parsing4.parsing_brandsite;

                SET FOREIGN_KEY_CHECKS = 1;
            """
    with connection.cursor() as cursor:
        cursor.execute(query)
    print(f'Скопированы данные из evsan_parsing4.parsing_brand в evsan_parsing42.parsing_brand.')

    from_scheme = 'evsan_parsing4'
    to_scheme = settings.DATABASES['default']['NAME']
    tables = (
        (f'{from_scheme}.parsing_site', f'{to_scheme}.parsing_site'),
        (f'{from_scheme}.parsing_sitepage', f'{to_scheme}.parsing_sitepage'),
        (f'{from_scheme}.parsing_sitepageparsing', f'{to_scheme}.parsing_sitepageparsing'),
        (f'{from_scheme}.parsing_siteproductpage', f'{to_scheme}.parsing_siteproductpage'),
        (f'{from_scheme}.parsing_sitepriceparsing', f'{to_scheme}.parsing_sitepriceparsing'),
    )
    # run_copy_data_between_tables(tables)
