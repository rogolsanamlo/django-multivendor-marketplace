from rest_framework import serializers

from apps.comment_scoring_favorites.models import (
    Comment,
    Favorite,
    Scoring,
)


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = [
            "id",
            "store_product",
            "commenting_user",
            "approving_user",
            "comment_text",
            "register_date",
            "is_active",
            "comment_parent",
        ]
        read_only_fields = [
            "id",
            "commenting_user",
            "approving_user",
            "register_date",
            "is_active",
        ]

    def validate_comment_text(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "متن نظر نمی‌تواند خالی باشد."
            )

        return value

    def validate(self, attrs):
        parent = attrs.get("comment_parent")
        store_product = attrs.get("store_product")

        if (
            parent
            and store_product
            and parent.store_product_id != store_product.id
        ):
            raise serializers.ValidationError(
                {
                    "comment_parent": (
                        "پاسخ باید مربوط به همان کالا باشد."
                    )
                }
            )

        return attrs


class ScoringSerializer(serializers.ModelSerializer):

    class Meta:
        model = Scoring
        fields = [
            "id",
            "store_product",
            "scoring_user",
            "register_date",
            "score",
        ]
        read_only_fields = [
            "id",
            "scoring_user",
            "register_date",
        ]

    def validate_score(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError(
                "امتیاز باید بین 0 و 5 باشد."
            )

        return value


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = [
            "id",
            "store_product",
            "favorite_user",
            "register_date",
        ]
        read_only_fields = [
            "id",
            "favorite_user",
            "register_date",
        ]