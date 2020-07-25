from django.db import models


class RingoManufacturer(models.Model):
    manufacturer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    image = models.CharField(max_length=255, blank=True, null=True)
    sort_order = models.IntegerField()
    status = models.IntegerField()

    def __str__(self):
        return self.name

    def save(self):
        return None

    class Meta:
        managed = False
        db_table = 'ringo_manufacturer'
        verbose_name = 'Бренд'
        verbose_name_plural = 'Производители'


class RingoOptionValueDescription(models.Model):
    option_value_id = models.IntegerField(primary_key=True)
    language_id = models.IntegerField()
    option_id = models.IntegerField()
    name = models.CharField(max_length=128)

    def save(self):
        return None

    class Meta:
        managed = False
        db_table = 'ringo_option_value_description'
        unique_together = (('option_value_id', 'language_id'),)


class RingoProduct(models.Model):
    product_id = models.AutoField(primary_key=True, verbose_name='Id товара')
    model = models.CharField(max_length=64, verbose_name='Артикул')
    sku = models.CharField(max_length=64, verbose_name='Код')
    upc = models.CharField(max_length=12)
    ean = models.CharField(max_length=14)
    jan = models.CharField(max_length=13)
    isbn = models.CharField(max_length=17)
    mpn = models.CharField(max_length=64)
    location = models.CharField(max_length=128)
    quantity = models.IntegerField()
    stock_status_id = models.IntegerField()
    image = models.CharField(max_length=255, blank=True, null=True)
    manufacturer_id = models.ForeignKey(RingoManufacturer, db_column='manufacturer_id', on_delete=models.PROTECT, verbose_name='Бренд')
    shipping = models.IntegerField()
    price = models.DecimalField(max_digits=15, decimal_places=4, verbose_name='Цена')
    points = models.IntegerField()
    tax_class_id = models.IntegerField()
    date_available = models.DateField()
    weight = models.DecimalField(max_digits=15, decimal_places=8)
    weight_class_id = models.IntegerField()
    length = models.DecimalField(max_digits=15, decimal_places=8)
    width = models.DecimalField(max_digits=15, decimal_places=8)
    height = models.DecimalField(max_digits=15, decimal_places=8)
    length_class_id = models.IntegerField()
    subtract = models.IntegerField()
    minimum = models.IntegerField()
    sort_order = models.IntegerField()
    status = models.IntegerField()
    viewed = models.IntegerField()
    date_added = models.DateTimeField()
    date_modified = models.DateTimeField()

    def __str__(self):
        return str(self.product_id)

    class Meta:
        managed = False
        db_table = 'ringo_product'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class RingoProductDescription(models.Model):
    product_id = models.OneToOneField(RingoProduct, db_column='product_id', primary_key=True, on_delete=models.PROTECT,
                                      related_name='productdescription', verbose_name='Id товара')
    language_id = models.IntegerField()
    name = models.CharField(max_length=255, verbose_name='Наименование')
    description = models.TextField()
    tag = models.TextField()
    meta_title = models.CharField(max_length=255)
    meta_description = models.CharField(max_length=255)
    meta_keyword = models.CharField(max_length=255)
    meta_h1 = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def save(self):
        return None

    class Meta:
        managed = False
        db_table = 'ringo_product_description'
        unique_together = (('product_id', 'language_id'),)


class RingoProductOptionValue(models.Model):
    product_option_value_id = models.AutoField(primary_key=True)
    product_option_id = models.IntegerField()
    product_id = models.ForeignKey(RingoProductDescription, db_column='product_id', on_delete=models.PROTECT, verbose_name='Товар с данной опцией')
    option_id = models.IntegerField()
    option_value_id = models.ForeignKey(RingoOptionValueDescription, db_column='option_value_id',
                                        on_delete=models.PROTECT, verbose_name='Товар-опция')
    quantity = models.IntegerField()
    subtract = models.IntegerField()
    price = models.DecimalField(max_digits=15, decimal_places=4, verbose_name='Цена')
    price_prefix = models.CharField(max_length=1)
    points = models.IntegerField()
    points_prefix = models.CharField(max_length=1)
    weight = models.DecimalField(max_digits=15, decimal_places=8)
    weight_prefix = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'ringo_product_option_value'
        verbose_name = 'Товар-опция'
        verbose_name_plural = 'Товары в опциях'
