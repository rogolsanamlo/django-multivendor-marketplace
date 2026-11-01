from django.db import transaction
from django.db.models import Q, Sum
from rest_framework import generics, serializers

from apps.api.pagination import OptionalPageNumberPagination
from apps.api.permissions import IsAuthenticatedUser, IsStoreOwner
from apps.api.serializers.warehouses import (
    WarehouseTypeSerializer,
    WarehouseSerializer,
)
from apps.products.models import StoreProduct
from apps.warehouses.models import (
    WarehouseType,
    Warehouse,
)

def get_stock(store_product):
    """Current stock = total incoming quantity - total outgoing quantity."""

    totals = Warehouse.objects.filter(
        store_product=store_product
    ).aggregate(
        total_in=Sum(
            "qty",
            filter=Q(warehouse_type__code=WarehouseType.INPUT),
        ),
        total_out=Sum(
            "qty",
            filter=Q(warehouse_type__code=WarehouseType.OUTPUT),
        ),
    )

    return (totals["total_in"] or 0) - (totals["total_out"] or 0)


def owner_warehouses(user):

    return Warehouse.objects.filter(
        store_product__store__user=user
    ).select_related(
        "warehouse_type",
        "store_product",
        "store_product__store",
        "user_registered",
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


class WarehouseListCreateAPIView(generics.ListCreateAPIView):

    serializer_class = WarehouseSerializer
    pagination_class = OptionalPageNumberPagination
    permission_classes = [
        IsStoreOwner,
    ]

    def get_queryset(self):

        return owner_warehouses(self.request.user)

    def perform_create(self, serializer):

        data = serializer.validated_data

        with transaction.atomic():
            # Lock the product row to prevent concurrent outgoing transactions
            # from reducing the stock below zero.
            StoreProduct.objects.select_for_update().get(
                pk=data["store_product"].pk
            )

            if data["warehouse_type"].code == WarehouseType.OUTPUT:
                stock = get_stock(data["store_product"])

                if data["qty"] > stock:
                    raise serializers.ValidationError({
                        "qty": (
                            "موجودی کافی نیست. "
                            f"موجودی فعلی: {stock}"
                        )
                    })

            serializer.save(
                user_registered=self.request.user
            )


class WarehouseDetailAPIView(generics.RetrieveAPIView):
    """
    Warehouse records are read-only.
    To correct stock, create a new incoming or outgoing record.
    """

    serializer_class = WarehouseSerializer
    permission_classes = [
        IsStoreOwner,
    ]

    def get_queryset(self):

        return owner_warehouses(self.request.user)
