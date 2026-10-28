from rest_framework import generics

from apps.api.permissions import (
    IsAuthenticatedUser,
    IsStoreOwner,
)
from apps.api.serializers.discounts import (
    CouponSerializer,
    DiscountBasketDetailsSerializer,
    DiscountBasketSerializer,
)
from apps.discounts.models import (
    Coupon,
    DiscountBasket,
    DiscountBasketDetails,
)


class CouponListCreateAPIView(generics.ListCreateAPIView):

    serializer_class = CouponSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsStoreOwner()]

        return [IsAuthenticatedUser()]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Coupon.objects.none()

        return Coupon.objects.filter(
            store__user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(
            store=self.request.user.store
        )


class CouponDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = CouponSerializer
    permission_classes = [
        IsStoreOwner
    ]

    def get_queryset(self):
        return Coupon.objects.filter(
            store__user=self.request.user
        )


class DiscountBasketListAPIView(
    generics.ListAPIView
):

    serializer_class = DiscountBasketSerializer
    permission_classes = [
        IsAuthenticatedUser
    ]

    def get_queryset(self):
        return DiscountBasket.objects.filter(
            is_active=True
        )


class DiscountBasketDetailAPIView(
    generics.RetrieveAPIView
):

    serializer_class = DiscountBasketSerializer
    permission_classes = [
        IsAuthenticatedUser
    ]

    def get_queryset(self):
        return DiscountBasket.objects.filter(
            is_active=True
        )


class DiscountBasketDetailsListAPIView(
    generics.ListAPIView
):

    serializer_class = DiscountBasketDetailsSerializer
    permission_classes = [
        IsAuthenticatedUser
    ]

    def get_queryset(self):
        return DiscountBasketDetails.objects.filter(
            discount_basket__is_active=True
        ).select_related(
            "discount_basket",
            "store_product",
            "store_product__product",
            "store_product__store",
        )