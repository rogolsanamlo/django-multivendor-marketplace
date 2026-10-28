from django.urls import path

from apps.api.views.orders import (
    MyOrderListAPIView,
    MyOrderDetailAPIView,
    StoreOrderListAPIView,
    StoreOrderDetailAPIView,
    PaymentTypeListAPIView,
    OrderStateListAPIView,
)


urlpatterns = [

    path(
        "orders/",
        MyOrderListAPIView.as_view(),
        name="order-list",
    ),

    path(
        "orders/<int:pk>/",
        MyOrderDetailAPIView.as_view(),
        name="order-detail",
    ),

    path(
        "store-orders/",
        StoreOrderListAPIView.as_view(),
        name="store-order-list",
    ),

    path(
        "store-orders/<int:pk>/",
        StoreOrderDetailAPIView.as_view(),
        name="store-order-detail",
    ),

    path(
        "payment-types/",
        PaymentTypeListAPIView.as_view(),
        name="payment-type-list",
    ),

    path(
        "order-states/",
        OrderStateListAPIView.as_view(),
        name="order-state-list",
    ),
]