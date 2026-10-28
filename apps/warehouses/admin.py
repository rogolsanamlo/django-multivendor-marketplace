from django.contrib import admin
from django.core import serializers
from django.http import HttpResponse

from .models import Warehouse, WarehouseType


@admin.action(description="خروجی JSON از انبارهای انتخاب شده")
def export_json(modeladmin, request, queryset):
    response = HttpResponse(
        content_type="application/json"
    )

    serializers.serialize(
        "json",
        queryset,
        stream=response,
    )

    return response


@admin.register(WarehouseType)
class WarehouseTypeAdmin(admin.ModelAdmin):

    list_display = [
        "warehouse_type_title",
        "code",
    ]

    search_fields = [
        "warehouse_type_title",
        "code",
    ]


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):

    list_display = [
        "store_product",
        "warehouse_type",
        "user_registered",
        "qty",
        "price",
        "register_date",
    ]

    list_filter = [
        "warehouse_type",
        "register_date",
    ]

    search_fields = [
        "store_product__product__product_name",
        "store_product__store__store_name",
        "user_registered__mobile_number",
    ]

    readonly_fields = [
        "register_date",
    ]

    actions = [
        export_json,
    ]