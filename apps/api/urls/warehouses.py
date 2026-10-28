from django.urls import path

from apps.api.views.warehouses import (
    WarehouseTypeListAPIView,
    WarehouseTypeDetailAPIView,
    WarehouseListCreateAPIView,
    WarehouseDetailAPIView,
)


urlpatterns = [

    path(
        "warehouse-types/",
        WarehouseTypeListAPIView.as_view(),
        name="warehouse-type-list",
    ),

    path(
        "warehouse-types/<int:pk>/",
        WarehouseTypeDetailAPIView.as_view(),
        name="warehouse-type-detail",
    ),

    path(
        "warehouses/",
        WarehouseListCreateAPIView.as_view(),
        name="warehouse-list",
    ),

    path(
        "warehouses/<int:pk>/",
        WarehouseDetailAPIView.as_view(),
        name="warehouse-detail",
    ),
]