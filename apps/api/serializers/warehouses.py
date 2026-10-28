from rest_framework import serializers

from apps.warehouses.models import (
    WarehouseType,
    Warehouse,
)


class WarehouseTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = WarehouseType
        fields = [
            "id",
            "warehouse_type_title",
            "code",
        ]
        read_only_fields = fields


class WarehouseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Warehouse
        fields = [
            "id",
            "warehouse_type",
            "user_registered",
            "store_product",
            "qty",
            "price",
            "register_date",
        ]
        read_only_fields = [
            "id",
            "user_registered",
            "register_date",
        ]

    def validate_qty(self, value):

        if value <= 0:
            raise serializers.ValidationError(
                "تعداد باید بیشتر از صفر باشد."
            )

        return value

    def validate_store_product(self, value):

        request = self.context["request"]

        store = getattr(
            request.user,
            "store",
            None
        )

        if store is None:
            raise serializers.ValidationError(
                "کاربر فروشگاه ندارد."
            )

        if value.store != store:
            raise serializers.ValidationError(
                "این کالا متعلق به فروشگاه شما نیست."
            )

        return value