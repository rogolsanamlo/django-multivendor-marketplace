from django.contrib import admin

from .models import Order, OrderDetails, OrderState, PaymentType


class OrderDetailsInline(admin.TabularInline):
    model = OrderDetails
    extra = 0
    autocomplete_fields = ('store_product',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'order_code',
        'customer',
        'store',
        'is_finally',
        'order_state',
        'register_date',
    )

    list_filter = (
        'is_finally',
        'order_state',
        'store',
        'register_date',
    )

    search_fields = (
        'order_code',
        'customer__user__mobile_number',
        'customer__user__family',
        'store__store_name',
    )

    ordering = ('-register_date', '-id')

    inlines = [OrderDetailsInline]


@admin.register(PaymentType)
class PaymentTypeAdmin(admin.ModelAdmin):
    list_display = ('payment_title',)


@admin.register(OrderState)
class OrderStateAdmin(admin.ModelAdmin):
    list_display = ('order_state_title',)
