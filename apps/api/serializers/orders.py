from rest_framework import serializers

from apps.orders.models import (
    Order,
    OrderDetails,
    OrderState,
    PaymentType,
)


class PaymentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentType
        fields = [
            "id",
            "payment_title",
        ]


class OrderStateSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderState
        fields = [
            "id",
            "order_state_title",
        ]


class OrderDetailSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source="store_product.product.product_name",
        read_only=True,
    )

    class Meta:
        model = OrderDetails
        fields = [
            "id",
            "store_product",
            "product_name",
            "qty",
            "price",
        ]
        read_only_fields = [
            "id",
            "product_name",
            "price",
        ]


class OrderSerializer(serializers.ModelSerializer):

    details = OrderDetailSerializer(
        many=True,
        read_only=True,
    )

    payment_type = PaymentTypeSerializer(
        read_only=True,
    )

    order_state = OrderStateSerializer(
        read_only=True,
    )

    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_code",
            "customer",
            "store",
            "register_date",
            "update_date",
            "is_finally",
            "discount",
            "description",
            "payment_type",
            "order_state",
            "details",
            "total_price",
        ]
        read_only_fields = [
            "id",
            "order_code",
            "customer",
            "store",
            "register_date",
            "update_date",
            "is_finally",
            "details",
            "total_price",
        ]

    def get_total_price(self, obj):
        return obj.get_order_total_price()