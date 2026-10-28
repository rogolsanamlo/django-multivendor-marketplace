from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

from apps.accounts.models import Store
from apps.products.models import StoreProduct


class Coupon(models.Model):

    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="coupons",
        verbose_name="فروشگاه",
    )

    coupon_code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="کد کوپن",
    )

    start_date = models.DateTimeField(
        verbose_name="تاریخ شروع",
    )

    end_date = models.DateTimeField(
        verbose_name="تاریخ پایان",
    )

    discount = models.IntegerField(
        verbose_name="درصد تخفیف",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    is_active = models.BooleanField(
        default=False,
        verbose_name="وضعیت",
    )

    class Meta:
        verbose_name = "کوپن تخفیف"
        verbose_name_plural = "کوپن‌ها"

    def __str__(self):
        return self.coupon_code


class DiscountBasket(models.Model):

    discount_title = models.CharField(
        max_length=100,
        verbose_name="عنوان سبد تخفیف",
    )

    start_date = models.DateTimeField(
        verbose_name="تاریخ شروع",
    )

    end_date = models.DateTimeField(
        verbose_name="تاریخ پایان",
    )

    discount = models.IntegerField(
        verbose_name="درصد تخفیف",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    is_active = models.BooleanField(
        default=False,
        verbose_name="وضعیت",
    )

    class Meta:
        verbose_name = "سبد تخفیف"
        verbose_name_plural = "سبدهای تخفیف"

    def __str__(self):
        return self.discount_title


class DiscountBasketDetails(models.Model):

    discount_basket = models.ForeignKey(
        DiscountBasket,
        on_delete=models.CASCADE,
    )

    store_product = models.ForeignKey(
        StoreProduct,
        on_delete=models.CASCADE,
        related_name="discounts",
    )

    class Meta:
        verbose_name = "جزئیات سبد تخفیف"
        verbose_name_plural = "جزئیات سبدهای تخفیف"
        unique_together = (
            "discount_basket",
            "store_product",
        )