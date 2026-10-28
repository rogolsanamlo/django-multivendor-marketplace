from rest_framework import generics

from apps.api.permissions import IsAuthenticatedUser, IsStoreOwner
from apps.api.serializers.warehouses import (
    WarehouseTypeSerializer,
    WarehouseSerializer,
)
from apps.warehouses.models import (
    WarehouseType,
    Warehouse,
)


class WarehouseTypeListAPIView(generics.ListAPIView):

    queryset = WarehouseType.objects.all()
    serializer_class = WarehouseTypeSerializer
    permission_classes = [
        IsAuthenticatedUser,
    ]


class WarehouseTypeDetailAPIView(generics.RetrieveAPIView):

    queryset = WarehouseType.objects.all()
    serializer_class = WarehouseTypeSerializer
    permission_classes = [
        IsAuthenticatedUser,
    ]


class WarehouseListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = WarehouseSerializer
    permission_classes = [
        IsStoreOwner,
    ]

    def get_queryset(self):

        return Warehouse.objects.filter(
            store_product__store__user=self.request.user
        ).select_related(
            "warehouse_type",
            "store_product",
            "store_product__store",
            "user_registered",
        )

    def perform_create(self, serializer):

        serializer.save(
            user_registered=self.request.user
        )


class WarehouseDetailAPIView(
    generics.RetrieveDestroyAPIView
):

    serializer_class = WarehouseSerializer
    permission_classes = [
        IsStoreOwner,
    ]

    def get_queryset(self):

        return Warehouse.objects.filter(
            store_product__store__user=self.request.user
        ).select_related(
            "warehouse_type",
            "store_product",
            "store_product__store",
            "user_registered",
        )