from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.serializers.orders import (
    OrderSerializer,
    OrderStateSerializer,
    PaymentTypeSerializer,
)
from apps.orders.models import (
    Order,
    OrderState,
    PaymentType,
)


class MyOrderListAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        orders = (
            Order.objects
            .filter(
                customer__user=request.user
            )
            .select_related(
                "customer",
                "store",
                "payment_type",
                "order_state",
            )
            .prefetch_related(
                "details__store_product"
            )
            .order_by(
                "-register_date",
                "-id",
            )
        )

        serializer = OrderSerializer(
            orders,
            many=True,
        )

        return Response(serializer.data)


class MyOrderDetailAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, pk):
        order = get_object_or_404(
            Order.objects
            .select_related(
                "customer",
                "store",
                "payment_type",
                "order_state",
            )
            .prefetch_related(
                "details__store_product"
            ),
            pk=pk,
            customer__user=request.user,
        )

        serializer = OrderSerializer(order)

        return Response(serializer.data)


class StoreOrderListAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        store = getattr(
            request.user,
            "store",
            None,
        )

        if store is None or not store.is_active:
            return Response(
                {
                    "detail": "شما صاحب یک فروشگاه فعال نیستید."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        orders = (
            Order.objects
            .filter(
                store=store
            )
            .select_related(
                "customer",
                "store",
                "payment_type",
                "order_state",
            )
            .prefetch_related(
                "details__store_product"
            )
            .order_by(
                "-register_date",
                "-id",
            )
        )

        serializer = OrderSerializer(
            orders,
            many=True,
        )

        return Response(serializer.data)


class StoreOrderDetailAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, pk):
        store = getattr(
            request.user,
            "store",
            None,
        )

        if store is None or not store.is_active:
            return Response(
                {
                    "detail": "شما صاحب یک فروشگاه فعال نیستید."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        order = get_object_or_404(
            Order.objects
            .select_related(
                "customer",
                "store",
                "payment_type",
                "order_state",
            )
            .prefetch_related(
                "details__store_product"
            ),
            pk=pk,
            store=store,
        )

        serializer = OrderSerializer(order)

        return Response(serializer.data)


class PaymentTypeListAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        payment_types = PaymentType.objects.all()

        serializer = PaymentTypeSerializer(
            payment_types,
            many=True,
        )

        return Response(serializer.data)


class OrderStateListAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        order_states = OrderState.objects.all()

        serializer = OrderStateSerializer(
            order_states,
            many=True,
        )

        return Response(serializer.data)