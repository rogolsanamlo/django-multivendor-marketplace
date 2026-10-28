from rest_framework import serializers

from apps.discounts.models import (
    Coupon,
    DiscountBasket,
    DiscountBasketDetails,
)
from apps.discounts.services import get_price_by_discount


class CouponSerializer(serializers.ModelSerializer):

    class Meta:
        model = Coupon
        fields = [
            "id",
            "store",
            "coupon_code",
            "start_date",
            "end_date",
            "discount",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "store",
        ]

    def validate_discount(self, value):
        if not 0 <= value <= 100:
            raise serializers.ValidationError(
                "درصد تخفیف باید بین ۰ تا ۱۰۰ باشد."
            )

        return value


class DiscountBasketSerializer(serializers.ModelSerializer):

    class Meta:
        model = DiscountBasket
        fields = [
            "id",
            "discount_title",
            "start_date",
            "end_date",
            "discount",
            "is_active",
        ]
        read_only_fields = fields


class DiscountBasketDetailsSerializer(
    serializers.ModelSerializer
):

    discount_basket = DiscountBasketSerializer(
        read_only=True
    )

    store_product_id = serializers.IntegerField(
        source="store_product.id",
        read_only=True,
    )

    product_name = serializers.CharField(
        source="store_product.product.product_name",
        read_only=True,
    )

    store_name = serializers.CharField(
        source="store_product.store.store_name",
        read_only=True,
    )

    original_price = serializers.DecimalField(
        source="store_product.price",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = DiscountBasketDetails

        fields = [
            "id",
            "discount_basket",
            "store_product_id",
            "product_name",
            "store_name",
            "original_price",
            "discounted_price",
        ]
        read_only_fields = fields

    def get_discounted_price(self, obj):
        return get_price_by_discount(
            obj.store_product
        )