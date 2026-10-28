from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

import jdatetime

from apps.accounts.models import UserProfile
from apps.orders.models import Order


class Payment(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payment_order",
        verbose_name="سفارش",
    )

    customer = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="payment_customer",
        verbose_name="مشتری",
    )

    register_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="تاریخ پرداخت",
    )

    update_date = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ ویرایش پرداخت",
    )

    amount = models.IntegerField(
        verbose_name="مبلغ پرداخت",
        validators=[
            MinValueValidator(0),
        ],
    )

    description = models.TextField(
        verbose_name="توضیحات پرداخت",
        blank=True,
    )

    is_finally = models.BooleanField(
        default=False,
        verbose_name="وضعیت پرداخت",
    )

    status_code = models.IntegerField(
        verbose_name="کد وضعیت درگاه پرداخت",
        null=True,
        blank=True,
    )

    ref_id = models.CharField(
        max_length=50,
        verbose_name="شماره پیگیری پرداخت",
        null=True,
        blank=True,
    )

    authority = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="شناسه پرداخت زرین پال",
    )

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت ها"

    def __str__(self):
        return (
            f"{self.order}\t"
            f"{self.customer}\t"
            f"{self.ref_id}"
        )

    def payment_register_date_jalali_type(self):
        return jdatetime.datetime.fromgregorian(
            datetime=self.register_date
        )

    payment_register_date_jalali_type.short_description = "زمان انتشار"

