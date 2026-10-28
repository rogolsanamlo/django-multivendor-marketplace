from rest_framework import serializers


class TopProductSerializer(serializers.Serializer):

    store_product = serializers.IntegerField()

    store_product__product__product_name = (
        serializers.CharField()
    )

    total_quantity = serializers.IntegerField()


class TopCategorySerializer(serializers.Serializer):

    store_product__product__product_group__group_title = (
        serializers.CharField()
    )

    total_quantity = serializers.IntegerField()


class DailySalesSerializer(serializers.Serializer):

    order__register_date = serializers.DateField()

    total_sales = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
    )


class MonthlyIncomeSerializer(serializers.Serializer):

    month = serializers.DateTimeField()

    income = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
    )


class LowStockProductSerializer(serializers.Serializer):

    store_product = serializers.IntegerField()

    product_name = serializers.CharField()

    qty = serializers.IntegerField()


class LastOrderSerializer(serializers.Serializer):

    id = serializers.IntegerField()

    order_code = serializers.UUIDField()

    register_date = serializers.DateField()

    is_finally = serializers.BooleanField()


class TopCustomerSerializer(serializers.Serializer):

    order__customer = serializers.IntegerField()

    order__customer__user__name = serializers.CharField()

    order__customer__user__family = serializers.CharField()

    total_orders = serializers.IntegerField()

    total_amount = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
    )


class LastSevenDaysSalesSerializer(serializers.Serializer):

    date = serializers.DateField()

    amount = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
    )