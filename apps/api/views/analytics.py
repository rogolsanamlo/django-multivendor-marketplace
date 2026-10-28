from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Store
from apps.analytics.services import (
    get_active_products_count,
    get_available_products_count,
    get_average_order_amount,
    get_daily_sales,
    get_last_7_days_sales,
    get_last_orders,
    get_low_stock_products,
    get_monthly_income,
    get_new_customers_this_month,
    get_orders_count,
    get_products_without_sales,
    get_store_profit,
    get_today_sales,
    get_top_categories,
    get_top_customers,
    get_top_products,
    get_total_sales,
)
from apps.api.permissions import (
    IsAuthenticatedUser,
    IsStoreOwner,
)
from apps.api.serializers.analytics import (
    DailySalesSerializer,
    LastOrderSerializer,
    LastSevenDaysSalesSerializer,
    LowStockProductSerializer,
    MonthlyIncomeSerializer,
    TopCategorySerializer,
    TopCustomerSerializer,
    TopProductSerializer,
)


class AnalyticsDashboardAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
        IsStoreOwner,
    ]

    def get(self, request, store_id):
        store = get_object_or_404(
            Store,
            id=store_id,
            user=request.user,
            is_active=True,
        )

        data = {
            "total_sales": get_total_sales(store),
            "today_sales": get_today_sales(store),
            "orders_count": get_orders_count(store),
            "active_products_count": (
                get_active_products_count(store)
            ),
            "available_products_count": (
                get_available_products_count(store)
            ),
            "new_customers_this_month": (
                get_new_customers_this_month(store)
            ),
            "average_order_amount": (
                get_average_order_amount(store)
            ),
            "store_profit": get_store_profit(store),
        }

        return Response(data)


class TopProductsAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
        IsStoreOwner,
    ]

    def get(self, request, store_id):
        store = get_object_or_404(
            Store,
            id=store_id,
            user=request.user,
            is_active=True,
        )

        result = get_top_products(store)

        serializer = TopProductSerializer(
            result,
            many=True,
        )

        return Response(serializer.data)


class TopCategoriesAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
        IsStoreOwner,
    ]

    def get(self, request, store_id):
        store = get_object_or_404(
            Store,
            id=store_id,
            user=request.user,
            is_active=True,
        )

        result = get_top_categories(store)

        serializer = TopCategorySerializer(
            result,
            many=True,
        )

        return Response(serializer.data)


class DailySalesAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
        IsStoreOwner,
    ]

    def get(self, request, store_id):
        store = get_object_or_404(
            Store,
            id=store_id,
            user=request.user,
            is_active=True,
        )

        result = get_daily_sales(store)

        serializer = DailySalesSerializer(
            result,
            many=True,
        )

        return Response(serializer.data)


class ProductsWithoutSalesAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
        IsStoreOwner,
    ]

    def get(self, request, store_id):
        store = get_object_or_404(
            Store,
            id=store_id,
            user=request.user,
            is_active=True,
        )

        result = get_products_without_sales(store)

        data = [
            {
                "id": item.id,
                "product_name": item.product.product_name,
                "price": item.price,
            }
            for item in result
        ]

        return Response(data)


class MonthlyIncomeAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
        IsStoreOwner,
    ]

    def get(self, request, store_id):
        store = get_object_or_404(
            Store,
            id=store_id,
            user=request.user,
            is_active=True,
        )

        result = get_monthly_income(store)

        serializer = MonthlyIncomeSerializer(
            result,
            many=True,
        )

        return Response(serializer.data)


class LowStockProductsAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
        IsStoreOwner,
    ]

    def get(self, request, store_id):
        store = get_object_or_404(
            Store,
            id=store_id,
            user=request.user,
            is_active=True,
        )

        result = get_low_stock_products(store)

        data = [
            {
                "store_product": item["store_product"].id,
                "product_name": (
                    item["store_product"]
                    .product
                    .product_name
                ),
                "qty": item["qty"],
            }
            for item in result
        ]

        serializer = LowStockProductSerializer(
            data,
            many=True,
        )

        return Response(serializer.data)


class LastOrdersAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
        IsStoreOwner,
    ]

    def get(self, request, store_id):
        store = get_object_or_404(
            Store,
            id=store_id,
            user=request.user,
            is_active=True,
        )

        result = get_last_orders(store)

        serializer = LastOrderSerializer(
            result,
            many=True,
        )

        return Response(serializer.data)


class TopCustomersAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
        IsStoreOwner,
    ]

    def get(self, request, store_id):
        store = get_object_or_404(
            Store,
            id=store_id,
            user=request.user,
            is_active=True,
        )

        result = get_top_customers(store)

        serializer = TopCustomerSerializer(
            result,
            many=True,
        )

        return Response(serializer.data)


class LastSevenDaysSalesAPIView(APIView):

    permission_classes = [
        IsAuthenticatedUser,
        IsStoreOwner,
    ]

    def get(self, request, store_id):
        store = get_object_or_404(
            Store,
            id=store_id,
            user=request.user,
            is_active=True,
        )

        result = get_last_7_days_sales(store)

        serializer = LastSevenDaysSalesSerializer(
            result,
            many=True,
        )

        return Response(serializer.data)