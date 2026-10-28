from rest_framework import serializers

from apps.accounts.models import (
    CustomUser,
    Store,
    UserProfile,
)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "mobile_number",
            "email",
            "name",
            "family",
        ]
        read_only_fields = [
            "id",
            "mobile_number",
        ]


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "address",
            "image_name",
        ]
        read_only_fields = [
            "user",
        ]


class StoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Store
        fields = [
            "id",
            "user",
            "store_name",
            "store_phone",
            "address",
            "created_at",
            "is_active",
            "slug",
            "description",
            "logo",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "is_active",
            "slug",
        ]