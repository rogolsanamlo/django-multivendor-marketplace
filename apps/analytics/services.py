from datetime import timedelta

from django.db.models import Avg, Count, F, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from apps.orders.models import Order, OrderDetails
from apps.products.models import StoreProduct
from apps.warehouses.models import Warehouse, WarehouseType


def get_top_products(store, limit=10):

    return (
        OrderDetails.objects
        .filter(
            order__store=store,
            order__is_finally=True,
            store_product__store=store,
        )
        .values(
            "store_product",
            "store_product__product__product_name",
        )
        .annotate(
            total_sales=Sum("qty")
        )
        .order_by("-total_sales")[:limit]
    )


def get_total_sales(store):

    result = (
        OrderDetails.objects
        .filter(
            order__store=store,
            order__is_finally=True,
            store_product__store=store,
        )
        .aggregate(
            total=Sum(
                F("price") * F("qty")
            )
        )
    )

    return result["total"] or 0


def get_today_sales(store):

    result = (
        OrderDetails.objects
        .filter(
            order__store=store,
            order__is_finally=True,
            store_product__store=store,
            order__register_date=timezone.now().date(),
        )
        .aggregate(
            total=Sum(
                F("price") * F("qty")
            )
        )
    )

    return result["total"] or 0


def get_top_categories(store):

    return (
        OrderDetails.objects
        .filter(
            order__store=store,
            order__is_finally=True,
            store_product__store=store,
        )
        .values(
            "store_product__product__product_group__group_title"
        )
        .annotate(
            total_sales=Sum("qty")
        )
        .order_by("-total_sales")
    )


def get_daily_sales(store):

    return (
        OrderDetails.objects
        .filter(
            order__store=store,
            order__is_finally=True,
            store_product__store=store,
        )
        .values(
            "order__register_date"
        )
        .annotate(
            total_sales=Sum(
                F("price") * F("qty")
            )
        )
        .order_by("order__register_date")
    )


def get_products_without_sales(store):

    return (
        StoreProduct.objects
        .filter(
            store=store
        )
        .annotate(
            total_sales=Sum(
                "orders_details__qty"
            )
        )
        .filter(
            total_sales__isnull=True
        )
    )


def get_monthly_income(store):

    return (
        OrderDetails.objects
        .filter(
            order__store=store,
            order__is_finally=True,
            store_product__store=store,
        )
        .annotate(
            month=TruncMonth(
                "order__register_date"
            )
        )
        .values(
            "month"
        )
        .annotate(
            income=Sum(
                F("price") * F("qty")
            )
        )
        .order_by("month")
    )


def get_low_stock_products(store):

    result = []

    store_products = (
        StoreProduct.objects
        .filter(
            store=store,
            is_active=True,
        )
        .select_related("product")
    )

    for item in store_products:

        qty = item.get_number_in_warehouse()

        if qty <= 10:
            result.append({
                "store_product": item,
                "qty": qty,
            })

    result.sort(
        key=lambda x: x["qty"]
    )

    return result


def get_orders_count(store):

    return (
        Order.objects
        .filter(
            store=store,
            is_finally=True,
        )
        .count()
    )


def get_active_products_count(store):

    return (
        StoreProduct.objects
        .filter(
            store=store,
            is_active=True,
        )
        .count()
    )


def get_available_products_count(store):

    count = 0

    products = (
        StoreProduct.objects
        .filter(
            store=store
        )
    )

    for item in products:

        if item.get_number_in_warehouse() > 0:
            count += 1

    return count


def get_store_profit(store):

    total_sell = get_total_sales(store)

    total_buy = (
        Warehouse.objects
        .filter(
            store_product__store=store,
            warehouse_type__code=WarehouseType.INPUT,
        )
        .aggregate(
            total=Sum(
                F("price") * F("qty")
            )
        )["total"] or 0
    )

    return {
        "sell": total_sell,
        "buy": total_buy,
        "profit": total_sell - total_buy,
    }


def get_last_orders(store, limit=10):

    return (
        Order.objects
        .filter(
            store=store,
            is_finally=True,
        )
        .select_related(
            "customer",
            "customer__user",
        )
        .prefetch_related(
            "details__store_product__product"
        )
        .order_by(
            "-register_date"
        )[:limit]
    )


def get_top_customers(store, limit=10):

    return (
        OrderDetails.objects
        .filter(
            order__store=store,
            order__is_finally=True,
            store_product__store=store,
        )
        .values(
            "order__customer",
            "order__customer__user__name",
            "order__customer__user__family",
        )
        .annotate(
            total_orders=Count(
                "order",
                distinct=True,
            ),
            total_amount=Sum(
                F("price") * F("qty")
            ),
        )
        .order_by(
            "-total_amount"
        )[:limit]
    )


def get_last_7_days_sales(store):

    today = timezone.now().date()

    result = []

    for i in range(6, -1, -1):

        day = today - timedelta(days=i)

        total = (
            OrderDetails.objects
            .filter(
                order__store=store,
                order__is_finally=True,
                store_product__store=store,
                order__register_date=day,
            )
            .aggregate(
                amount=Sum(
                    F("price") * F("qty")
                )
            )
        )

        result.append({
            "date": day,
            "amount": total["amount"] or 0,
        })

    return result


def get_new_customers_this_month(store):

    today = timezone.now()

    return (
        Order.objects
        .filter(
            store=store,
            is_finally=True,
            register_date__year=today.year,
            register_date__month=today.month,
        )
        .values(
            "customer"
        )
        .distinct()
        .count()
    )


def get_average_order_amount(store):

    result = (
        OrderDetails.objects
        .filter(
            order__store=store,
            order__is_finally=True,
            store_product__store=store,
        )
        .values(
            "order"
        )
        .annotate(
            order_total=Sum(
                F("price") * F("qty")
            )
        )
        .aggregate(
            avg=Avg("order_total")
        )
    )

    return int(
        result["avg"] or 0
    )