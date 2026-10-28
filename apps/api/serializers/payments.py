from rest_framework import serializers

from apps.payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "customer",
            "register_date",
            "update_date",
            "amount",
            "description",
            "is_finally",
            "status_code",
            "ref_id",
            "authority",
        ]

        read_only_fields = fields
