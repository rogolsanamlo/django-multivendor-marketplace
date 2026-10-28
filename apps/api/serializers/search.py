from rest_framework import serializers

from apps.products.models import StoreProduct


class SearchResultSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source="product.product_name",
        read_only=True
    )

    store_name = serializers.CharField(
        source="store.store_name",
        read_only=True
    )

    class Meta:
        model = StoreProduct
        fields = [
            "id",
            "product",
            "product_name",
            "store",
            "store_name",
            "price",
            "is_active",
        ]
        read_only_fields = fields