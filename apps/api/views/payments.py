from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.models import Payment
from apps.api.serializers.payments import PaymentSerializer


class PaymentListAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):

        payments = (
            Payment.objects
            .filter(
                customer__user=request.user
            )
            .select_related(
                "order",
                "customer",
            )
            .order_by(
                "-register_date",
                "-id",
            )
        )

        serializer = PaymentSerializer(
            payments,
            many=True,
        )

        return Response(serializer.data)


class PaymentDetailAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, pk):

        payment = get_object_or_404(
            Payment.objects.select_related(
                "order",
                "customer",
            ),
            pk=pk,
            customer__user=request.user,
        )

        serializer = PaymentSerializer(payment)

        return Response(serializer.data)