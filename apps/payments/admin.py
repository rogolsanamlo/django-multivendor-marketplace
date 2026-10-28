from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'order',
        'customer',
        'amount',
        'is_finally',
        'status_code',
        'ref_id',
        'register_date',
    )

    list_filter = (
        'is_finally',
        'register_date',
    )

    search_fields = (
        'ref_id',
        'authority',
        'customer__user__mobile_number',
    )

    ordering = ('-register_date', '-id')

    # Payment records come from the payment gateway; they are not edited by hand.
    readonly_fields = (
        'order',
        'customer',
        'amount',
        'description',
        'is_finally',
        'status_code',
        'ref_id',
        'authority',
    )

    def has_add_permission(self, request):
        return False
