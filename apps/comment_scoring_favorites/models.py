from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

from apps.accounts.models import CustomUser
from apps.products.models import StoreProduct


class Comment(models.Model):
    store_product = models.ForeignKey(
        StoreProduct,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="کالا",
    )

    commenting_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="comments_user1",
        verbose_name="کاربر نظر دهنده",
    )

    approving_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="comments_user2",
        verbose_name="کاربر تایید کننده نظر",
        null=True,
        blank=True,
    )

    comment_text = models.TextField(
        verbose_name="متن نظر",
    )

    register_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ درج",
    )

    is_active = models.BooleanField(
        default=False,
        verbose_name="وضعیت نظر",
    )

    comment_parent = models.ForeignKey(
        "Comment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comments_child",
        verbose_name="ارایه نظر",
    )

    def __str__(self):
        return f"{self.store_product}\t{self.commenting_user}"

    class Meta:
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"


class Scoring(models.Model):
    store_product = models.ForeignKey(
        StoreProduct,
        on_delete=models.CASCADE,
        related_name="scoring_product",
        verbose_name="کالای فروشگاه",
    )

    scoring_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="scoring_user1",
    )

    register_date = models.DateTimeField(
        auto_now_add=True,
    )

    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    def __str__(self):
        return (
            f"{self.store_product}"
            f" - "
            f"{self.scoring_user}"
        )

    class Meta:
        verbose_name = "امتیاز"
        verbose_name_plural = "امتیازات"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "store_product",
                    "scoring_user",
                ],
                name="unique_user_score",
            ),
        ]


class Favorite(models.Model):
    store_product = models.ForeignKey(
        StoreProduct,
        on_delete=models.CASCADE,
        related_name="favorite_products",
    )

    favorite_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="favorite_user1",
    )

    register_date = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.store_product}"
            f" - "
            f"{self.favorite_user}"
        )

    class Meta:
        verbose_name = "علاقه"
        verbose_name_plural = "علایق"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "store_product",
                    "favorite_user",
                ],
                name="unique_favorite",
            ),
        ]