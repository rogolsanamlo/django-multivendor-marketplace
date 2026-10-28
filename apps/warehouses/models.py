from django.db import models

from apps.accounts.models import CustomUser
from apps.products.models import StoreProduct


class WarehouseType(models.Model):

    INPUT = 'input'
    OUTPUT = 'output'

    WAREHOUSE_TYPE_CHOICES = [
        (INPUT, 'ورودی'),
        (OUTPUT, 'خروجی'),
    ]

    warehouse_type_title = models.CharField(
        max_length=50,
        verbose_name='نوع انبار'
    )

    code = models.CharField(
        max_length=20,
        choices=WAREHOUSE_TYPE_CHOICES,
        unique=True,
        verbose_name='کد نوع انبار'
    )

    def __str__(self):
        return self.warehouse_type_title

    class Meta:
        verbose_name = 'انبار'
        verbose_name_plural = 'انواع انبار'


class Warehouse(models.Model):

    warehouse_type = models.ForeignKey(
        WarehouseType,
        on_delete=models.CASCADE
    )

    user_registered = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    store_product = models.ForeignKey(
        StoreProduct,
        on_delete=models.CASCADE,
        related_name='warehouse_products'
    )

    qty = models.IntegerField()

    price = models.IntegerField(
        null=True,
        blank=True
    )

    register_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.warehouse_type}-{self.store_product}"

    class Meta:
        verbose_name = 'انبار'
        verbose_name_plural = 'انبارها'