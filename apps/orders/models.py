import uuid

from django.db import models
from django.utils import timezone

import utils
from apps.accounts.models import Store, UserProfile
from apps.products.models import StoreProduct


class PaymentType(models.Model):
    payment_title = models.CharField(
        max_length=50,
        verbose_name="نوع پرداخت",
    )

    def __str__(self):
        return self.payment_title

    class Meta:
        verbose_name = "نوع پرداخت"
        verbose_name_plural = "انواع روش پرداخت"


class OrderState(models.Model):
    order_state_title = models.CharField(
        max_length=50,
        verbose_name="عنوان وضعیت سفارش",
    )

    def __str__(self):
        return self.order_state_title

    class Meta:
        verbose_name = "وضعیت سفارش"
        verbose_name_plural = "انواع وضعیتهای سفارش"


class Order(models.Model):
    customer = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="مشتری",
    )

    register_date = models.DateField(
        default=timezone.now,
        verbose_name="تاریخ درج سفارش",
    )

    update_date = models.DateField(
        auto_now=True,
        verbose_name="تاریخ ویرایش سفارش",
    )

    is_finally = models.BooleanField(
        default=False,
        verbose_name="نهایی شده",
    )

    order_code = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="کد تولیدی برای سفارش",
    )

    discount = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        verbose_name="تخفیف روی فاکتور",
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات",
    )

    payment_type = models.ForeignKey(
        PaymentType,
        default=None,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="payment_types",
        verbose_name="نوع پرداخت",
    )

    order_state = models.ForeignKey(
        OrderState,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="orders_states",
        verbose_name="وضعیت سفارش",
    )

    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    def get_order_total_price(self):
        total = 0

        for item in self.details.all():
            total += item.price * item.qty

        order_final_price, delivery, tax = (
            utils.price_by_delivery_tax(
                total,
                self.discount or 0,
            )
        )

        return int(order_final_price * 10)

    def __str__(self):
        return f"{self.customer}\t{self.id}\t{self.is_finally}"

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارشات"


class OrderDetails(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="details",
        verbose_name="سفارش",
    )

    store_product = models.ForeignKey(
        StoreProduct,
        on_delete=models.CASCADE,
        related_name="orders_details",
        verbose_name="کالا",
    )

    qty = models.PositiveIntegerField(
        default=1,
        verbose_name="تعداد",
    )

    price = models.IntegerField(
        verbose_name="قیمت کالا در فاکتور",
    )

    def __str__(self):
        return (
            f"{self.order}\t"
            f"{self.store_product}\t"
            f"{self.qty}\t"
            f"{self.price}"
        )

    class Meta:
        verbose_name = 'جزئیات سفارش'
        verbose_name_plural = 'جزئیات سفارش‌ها'