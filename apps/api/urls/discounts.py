from django.urls import path

from apps.api.views.discounts import (
    CouponListCreateAPIView,
    CouponDetailAPIView,
    DiscountBasketListAPIView,
    DiscountBasketDetailAPIView,
    DiscountBasketDetailsListAPIView,
)


urlpatterns = [

    path(
        "coupons/",
        CouponListCreateAPIView.as_view(),
        name="coupon-list",
    ),

    path(
        "coupons/<int:pk>/",
        CouponDetailAPIView.as_view(),
        name="coupon-detail",
    ),

    path(
        "discount-baskets/",
        DiscountBasketListAPIView.as_view(),
        name="discount-basket-list",
    ),

    path(
        "discount-baskets/<int:pk>/",
        DiscountBasketDetailAPIView.as_view(),
        name="discount-basket-detail",
    ),

    path(
        "discount-basket-details/",
        DiscountBasketDetailsListAPIView.as_view(),
        name="discount-basket-details-list",
    ),
]