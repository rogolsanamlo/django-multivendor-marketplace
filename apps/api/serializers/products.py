from rest_framework import serializers

from apps.products.models import (
    Brand,
    Feature,
    FeatureValue,
    Product,
    ProductFeature,
    ProductGallery,
    ProductGroup,
    StoreProduct,
)


class BrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = [
            "id",
            "brand_title",
            "image_name",
            "slug",
        ]


class ProductGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductGroup
        fields = [
            "id",
            "group_title",
            "image_name",
            "is_active",
            "group_parent",
            "slug",
            "register_date",
            "published_date",
            "update_date",
        ]


class FeatureValueSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeatureValue
        fields = [
            "id",
            "value_title",
            "feature",
        ]


class FeatureSerializer(serializers.ModelSerializer):

    class Meta:
        model = Feature
        fields = [
            "id",
            "feature_name",
            "product_group",
        ]


class ProductFeatureSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductFeature
        fields = [
            "id",
            "product",
            "feature",
            "value",
            "filter_value",
        ]


class ProductGallerySerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductGallery
        fields = [
            "id",
            "product",
            "image_name",
        ]


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = [
            "id",
            "product_name",
            "image_name",
            "product_group",
            "brand",
            "is_active",
            "slug",
            "summary_description",
            "description",
            "register_date",
            "update_date",
        ]
        read_only_fields = [
            "id",
            "register_date",
            "update_date",
        ]


class StoreProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = StoreProduct
        fields = [
            "id",
            "store",
            "product",
            "price",
            "is_active",
            "register_date",
            "update_date",
        ]
        read_only_fields = [
            "id",
            "store",
            "register_date",
            "update_date",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # کالا بعد از ساخت قابل تغییر نیست، پس برای PUT لازم نیست
        # دوباره فرستاده شود (ارسالش در validate رد می‌شود).
        if self.instance is not None:
            self.fields["product"].required = False

    def validate_price(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError(
                "قیمت باید بیشتر از صفر باشد."
            )

        return value

    def validate(self, attrs):
        if self.instance:
            if "store" in self.initial_data:
                raise serializers.ValidationError({
                    "store": "Store cannot be changed."
                })

            if "product" in self.initial_data:
                raise serializers.ValidationError({
                    "product": "Product cannot be changed."
                })

        return attrs