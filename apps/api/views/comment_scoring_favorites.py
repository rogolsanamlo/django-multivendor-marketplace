from rest_framework import generics, serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from apps.api.pagination import OptionalPageNumberPagination
from apps.api.permissions import IsAuthenticatedUser
from apps.api.serializers.comment_scoring_favorites import (
    CommentSerializer,
    FavoriteSerializer,
    ScoringSerializer,
)
from apps.comment_scoring_favorites.models import (
    Comment,
    Favorite,
    Scoring,
)


def filter_by_store_product(request, queryset):
    """فیلتر اختیاری ``?store_product=<id>`` روی لیست‌ها."""

    value = request.query_params.get("store_product")

    if value in (None, ""):
        return queryset

    try:
        return queryset.filter(store_product_id=int(value))
    except ValueError:
        raise serializers.ValidationError({
            "store_product": "شناسه‌ی کالا باید عدد باشد."
        })


class OwnerOnlyMixin:
    """
    فقط صاحب رکورد می‌تواند ویرایش/حذف کند (و در صورت
    ``read_requires_owner`` حتی بخواند)؛ در غیر این صورت ۴۰۳.
    """

    owner_field = None
    read_requires_owner = False
    read_denied_message = ""
    edit_denied_message = ""
    delete_denied_message = ""

    def get_object(self):
        obj = super().get_object()

        if getattr(obj, self.owner_field) == self.request.user:
            return obj

        if self.request.method in SAFE_METHODS:
            if self.read_requires_owner:
                raise PermissionDenied(self.read_denied_message)
            return obj

        if self.request.method == "DELETE":
            raise PermissionDenied(self.delete_denied_message)

        raise PermissionDenied(self.edit_denied_message)


# ---------------------------------------------------------------- Comment


class CommentListAPIView(generics.ListCreateAPIView):

    serializer_class = CommentSerializer
    pagination_class = OptionalPageNumberPagination
    permission_classes = [
        IsAuthenticatedUser,
    ]

    def get_queryset(self):
        queryset = Comment.objects.filter(
            is_active=True,
            store_product__is_active=True,
        ).select_related(
            "store_product",
            "commenting_user",
        )

        return filter_by_store_product(self.request, queryset)

    def perform_create(self, serializer):
        serializer.save(commenting_user=self.request.user)


class CommentDetailAPIView(
    OwnerOnlyMixin,
    generics.RetrieveUpdateDestroyAPIView,
):

    serializer_class = CommentSerializer
    queryset = Comment.objects.filter(is_active=True)
    permission_classes = [
        IsAuthenticatedUser,
    ]

    owner_field = "commenting_user"
    edit_denied_message = "شما اجازه ویرایش این نظر را ندارید."
    delete_denied_message = "شما اجازه حذف این نظر را ندارید."

    def perform_update(self, serializer):
        instance = serializer.instance

        changed = any(
            getattr(instance, field) != value
            for field, value in serializer.validated_data.items()
        )

        if changed:
            # نظر ویرایش‌شده باید دوباره تأیید شود.
            serializer.save(
                is_active=False,
                approving_user=None,
            )
        else:
            serializer.save()


# ---------------------------------------------------------------- Scoring


class ScoringListAPIView(generics.ListCreateAPIView):

    serializer_class = ScoringSerializer
    pagination_class = OptionalPageNumberPagination
    permission_classes = [
        IsAuthenticatedUser,
    ]

    def get_queryset(self):
        # هر کاربر فقط امتیازهای خودش را می‌بیند.
        queryset = Scoring.objects.filter(
            scoring_user=self.request.user
        ).select_related(
            "store_product",
            "scoring_user",
        )

        return filter_by_store_product(self.request, queryset)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        scoring, created = Scoring.objects.update_or_create(
            store_product=serializer.validated_data["store_product"],
            scoring_user=request.user,
            defaults={
                "score": serializer.validated_data["score"],
            },
        )

        return Response(
            self.get_serializer(scoring).data,
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            ),
        )


class ScoringDetailAPIView(
    OwnerOnlyMixin,
    generics.RetrieveUpdateDestroyAPIView,
):

    serializer_class = ScoringSerializer
    queryset = Scoring.objects.all()
    permission_classes = [
        IsAuthenticatedUser,
    ]

    owner_field = "scoring_user"
    read_requires_owner = True
    read_denied_message = "شما اجازه دسترسی به این امتیاز را ندارید."
    edit_denied_message = "شما اجازه ویرایش این امتیاز را ندارید."
    delete_denied_message = "شما اجازه حذف این امتیاز را ندارید."


# --------------------------------------------------------------- Favorite


class FavoriteListAPIView(generics.ListCreateAPIView):

    serializer_class = FavoriteSerializer
    pagination_class = OptionalPageNumberPagination
    permission_classes = [
        IsAuthenticatedUser,
    ]

    def get_queryset(self):
        return Favorite.objects.filter(
            favorite_user=self.request.user
        ).select_related(
            "store_product",
            "store_product__product",
            "store_product__store",
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        favorite, created = Favorite.objects.get_or_create(
            store_product=serializer.validated_data["store_product"],
            favorite_user=request.user,
        )

        data = self.get_serializer(favorite).data

        if not created:
            return Response(
                {
                    "detail": (
                        "این کالا قبلاً در لیست علاقه‌مندی‌ها "
                        "قرار دارد."
                    ),
                    "data": data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(data, status=status.HTTP_201_CREATED)


class FavoriteDetailAPIView(
    OwnerOnlyMixin,
    generics.RetrieveDestroyAPIView,
):

    serializer_class = FavoriteSerializer
    queryset = Favorite.objects.all()
    permission_classes = [
        IsAuthenticatedUser,
    ]

    owner_field = "favorite_user"
    read_requires_owner = True
    read_denied_message = (
        "شما اجازه دسترسی به این علاقه‌مندی را ندارید."
    )
    delete_denied_message = "شما اجازه حذف این علاقه‌مندی را ندارید."
