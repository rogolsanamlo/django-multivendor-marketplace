from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import CustomUser, UserProfile, Store
from apps.orders.models import Order, PaymentType, OrderState
from apps.payments.models import Payment


class PaymentAPITests(APITestCase):

    def setUp(self):

        self.user = self.create_user("09120000001")
        self.other_user = self.create_user("09120000002")

        self.customer = UserProfile.objects.get(
            user=self.user
        )

        self.other_customer = UserProfile.objects.get(
            user=self.other_user
        )

        self.payment_type = PaymentType.objects.create(
            payment_title="Online"
        )

        self.order_state = OrderState.objects.create(
            order_state_title="Pending"
        )

        self.store = self.create_store(
            self.user,
            "09120000003",
        )

        self.other_store = self.create_store(
            self.other_user,
            "09120000004",
        )

        self.order = Order.objects.create(
            customer=self.customer,
            payment_type=self.payment_type,
            order_state=self.order_state,
            store=self.store,
        )

        self.other_order = Order.objects.create(
            customer=self.other_customer,
            payment_type=self.payment_type,
            order_state=self.order_state,
            store=self.other_store,
        )

        self.payment = Payment.objects.create(
            order=self.order,
            customer=self.customer,
            amount=100000,
            description="Test payment",
            is_finally=True,
            status_code=100,
            ref_id="123456",
            authority="AUTH123",
        )

        self.other_payment = Payment.objects.create(
            order=self.other_order,
            customer=self.other_customer,
            amount=200000,
            description="Other payment",
            is_finally=True,
            status_code=100,
            ref_id="654321",
            authority="AUTH456",
        )

    def create_user(self, mobile):

        return CustomUser.objects.create_user(
            mobile_number=mobile,
            password="test123",
            email=f"{mobile}@example.com",
            name="Test",
            family="User",
        )

    def create_store(self, user, phone):

        return Store.objects.create(
            user=user,
            store_name=f"Store {user.mobile_number}",
            store_phone=phone,
            address="Test Address",
        )

    def test_unauthenticated_user_cannot_see_payments(self):

        url = reverse("api:payment-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_can_see_own_payments(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse("api:payment-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            self.payment.id,
        )

    def test_user_cannot_see_other_user_payment(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:payment-detail",
            kwargs={
                "pk": self.other_payment.id
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_user_can_see_own_payment_detail(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:payment-detail",
            kwargs={
                "pk": self.payment.id
            },
        )
        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.payment.id,
        )

    def test_payment_api_is_read_only(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse("api:payment-list")

        response = self.client.post(
            url,
            {
                "amount": 999999,
                "is_finally": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

