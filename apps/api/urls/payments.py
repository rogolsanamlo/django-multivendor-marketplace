from django.urls import path

from apps.api.views.payments import (
    PaymentListAPIView,
    PaymentDetailAPIView,
)


urlpatterns = [

    path(
        "payments/",
        PaymentListAPIView.as_view(),
        name="payment-list",
    ),

    path(
        "payments/<int:pk>/",
        PaymentDetailAPIView.as_view(),
        name="payment-detail",
    ),

]