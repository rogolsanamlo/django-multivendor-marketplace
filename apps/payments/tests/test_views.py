from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse

from apps.accounts.models import CustomUser
from apps.orders.models import Order
from apps.orders.tests.test_models import BaseOrderTest
from apps.payments.models import Payment


class ZarinPalPaymentViewTests(BaseOrderTest):

    def setUp(self):
        super().setUp()

        self.user.is_active = True
        self.user.save()

        self.client.force_login(
            self.user
        )

        self.url = reverse(
            "payments:zarinpal_payment",
            kwargs={
                "order_id": self.order.id,
            },
        )

    @patch("apps.payments.views.ZarinPal")
    def test_create_payment(self, mock_zarinpal):
        mock_zarinpal_instance = (
            mock_zarinpal.return_value
        )

        mock_zarinpal_instance.payments.create.return_value = {
            "data": {
                "authority": (
                    "A0000000000000000000000000000TEST"
                ),
            },
            "errors": [],
        }

        mock_zarinpal_instance.payments.generate_payment_url.return_value = (
            "https://payment.test/A0000000000000000000000000000TEST"
        )

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            response.url,
            "https://payment.test/A0000000000000000000000000000TEST",
        )

        payment = Payment.objects.get(
            order=self.order
        )

        self.assertEqual(
            payment.amount,
            self.order.get_order_total_price(),
        )

        self.assertEqual(
            payment.authority,
            "A0000000000000000000000000000TEST",
        )

    @patch("apps.payments.views.ZarinPal")
    def test_create_payment_without_data(
        self,
        mock_zarinpal,
    ):
        mock_zarinpal_instance = (
            mock_zarinpal.return_value
        )

        mock_zarinpal_instance.payments.create.return_value = {
            "errors": [],
        }

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            response.url,
            reverse(
                "payments:show_verify_message"
            ),
        )

        payment = Payment.objects.get(
            order=self.order
        )

        self.assertFalse(
            payment.is_finally
        )

        self.assertIsNone(
            payment.authority
        )

    @patch("apps.payments.views.ZarinPal")
    def test_create_payment_without_authority(
        self,
        mock_zarinpal,
    ):
        mock_zarinpal_instance = (
            mock_zarinpal.return_value
        )

        mock_zarinpal_instance.payments.create.return_value = {
            "data": {},
            "errors": [],
        }

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            response.url,
            reverse(
                "payments:show_verify_message"
            ),
        )

        payment = Payment.objects.get(
            order=self.order
        )

        self.assertFalse(
            payment.is_finally
        )

        self.assertIsNone(
            payment.authority
        )

    @patch("apps.payments.views.ZarinPal")
    def test_create_payment_zarinpal_error(
        self,
        mock_zarinpal,
    ):
        mock_zarinpal.side_effect = Exception(
            "ZarinPal connection failed"
        )

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            response.url,
            reverse(
                "payments:show_verify_message"
            ),
        )

        payment = Payment.objects.get(
            order=self.order
        )

        self.assertFalse(
            payment.is_finally
        )

        self.assertIsNone(
            payment.authority
        )

    def test_config_is_accepted_by_the_real_sdk(self):
        from zarinpal import ZarinPal

        from apps.payments.views import Config

        sdk = ZarinPal(
            Config(
                sandbox=True,
                merchant_id="XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
            )
        )

        self.assertTrue(hasattr(sdk, "payments"))
        self.assertTrue(hasattr(sdk, "verifications"))

    @override_settings(DEBUG=True)
    @patch("apps.payments.views.ZarinPal")
    def test_gateway_error_details_are_shown_in_debug(
        self,
        mock_zarinpal,
    ):
        mock_zarinpal.side_effect = Exception("boom")

        self.client.get(self.url)

        response = self.client.get(
            reverse("payments:show_verify_message")
        )

        self.assertContains(response, "boom")

    @override_settings(DEBUG=False)
    @patch("apps.payments.views.ZarinPal")
    def test_gateway_error_details_are_hidden_in_production(
        self,
        mock_zarinpal,
    ):
        mock_zarinpal.side_effect = Exception("boom")

        self.client.get(self.url)

        response = self.client.get(
            reverse("payments:show_verify_message")
        )

        self.assertNotContains(response, "boom")

    @patch("apps.payments.views.ZarinPal")
    def test_empty_email_is_not_sent_to_gateway(
        self,
        mock_zarinpal,
    ):
        self.user.email = ""
        self.user.save()

        instance = mock_zarinpal.return_value
        instance.payments.create.return_value = {
            "data": {"authority": "A0000000000000000000000000000TEST"}
        }
        instance.payments.generate_payment_url.return_value = (
            "https://sandbox.zarinpal.com/pg/StartPay/TEST"
        )

        self.client.get(self.url)

        payload = instance.payments.create.call_args[0][0]

        self.assertNotIn("email", payload)
        self.assertEqual(payload["currency"], "IRR")
        self.assertEqual(payload["mobile"], self.user.mobile_number)

    @patch("apps.payments.views.ZarinPal")
    def test_verify_payment_success(
        self,
        mock_zarinpal,
    ):
        payment = Payment.objects.create(
            order=self.order,
            customer=self.profile,
            amount=self.order.get_order_total_price(),
            description="Test payment",
            authority=(
                "A0000000000000000000000000000TEST"
            ),
        )

        mock_zarinpal_instance = (
            mock_zarinpal.return_value
        )

        mock_zarinpal_instance.verifications.verify.return_value = {
            "data": {
                "code": 100,
                "ref_id": 123456789,
            },
            "errors": [],
        }

        response = self.client.get(
            reverse(
                "payments:zarinpal_verify"
            ),
            {
                "Status": "OK",
                "Authority": payment.authority,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        payment.refresh_from_db()
        self.order.refresh_from_db()

        self.assertTrue(
            payment.is_finally
        )

        self.assertEqual(
            payment.status_code,
            100,
        )

        self.assertEqual(
            payment.ref_id,
            "123456789",
        )

        self.assertTrue(
            self.order.is_finally
        )

    @patch("apps.payments.views.ZarinPal")
    def test_verify_payment_already_verified(
        self,
        mock_zarinpal,
    ):
        payment = Payment.objects.create(
            order=self.order,
            customer=self.profile,
            amount=self.order.get_order_total_price(),
            description="Test payment",
            authority=(
                "A0000000000000000000000000001TEST"
            ),
        )

        mock_zarinpal_instance = (
            mock_zarinpal.return_value
        )

        mock_zarinpal_instance.verifications.verify.return_value = {
            "data": {
                "code": 101,
                "ref_id": 987654321,
            },
            "errors": [],
        }

        response = self.client.get(
            reverse(
                "payments:zarinpal_verify"
            ),
            {
                "Status": "OK",
                "Authority": payment.authority,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        payment.refresh_from_db()
        self.order.refresh_from_db()

        self.assertTrue(
            payment.is_finally
        )

        self.assertEqual(
            payment.status_code,
            101,
        )

        self.assertEqual(
            payment.ref_id,
            "987654321",
        )

        self.assertTrue(
            self.order.is_finally
        )

    @patch("apps.payments.views.ZarinPal")
    def test_verify_payment_failed(
        self,
        mock_zarinpal,
    ):
        payment = Payment.objects.create(
            order=self.order,
            customer=self.profile,
            amount=self.order.get_order_total_price(),
            description="Test payment",
            authority=(
                "A0000000000000000000000000002TEST"
            ),
        )

        mock_zarinpal_instance = (
            mock_zarinpal.return_value
        )

        mock_zarinpal_instance.verifications.verify.return_value = {
            "data": {
                "code": -1,
            },
            "errors": [],
        }

        response = self.client.get(
            reverse(
                "payments:zarinpal_verify"
            ),
            {
                "Status": "OK",
                "Authority": payment.authority,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        payment.refresh_from_db()
        self.order.refresh_from_db()

        self.assertFalse(
            payment.is_finally
        )

        self.assertEqual(
            payment.status_code,
            -1,
        )

        self.assertIsNone(
            payment.ref_id
        )

        self.assertFalse(
            self.order.is_finally
        )

    @patch("apps.payments.views.ZarinPal")
    def test_verify_payment_cancelled(
        self,
        mock_zarinpal,
    ):
        payment = Payment.objects.create(
            order=self.order,
            customer=self.profile,
            amount=self.order.get_order_total_price(),
            description="Test payment",
            authority=(
                "A0000000000000000000000000003TEST"
            ),
        )

        response = self.client.get(
            reverse(
                "payments:zarinpal_verify"
            ),
            {
                "Status": "NOK",
                "Authority": payment.authority,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        mock_zarinpal.return_value.verifications.verify.assert_not_called()

        payment.refresh_from_db()
        self.order.refresh_from_db()

        self.assertFalse(
            payment.is_finally
        )

        self.assertIsNone(
            payment.status_code
        )

        self.assertFalse(
            self.order.is_finally
        )

    @patch("apps.payments.views.ZarinPal")
    def test_verify_payment_invalid_authority(
        self,
        mock_zarinpal,
    ):
        response = self.client.get(
            reverse(
                "payments:zarinpal_verify"
            ),
            {
                "Status": "OK",
                "Authority": "INVALID_AUTHORITY",
            },
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        mock_zarinpal.return_value.verifications.verify.assert_not_called()

    @patch("apps.payments.views.ZarinPal")
    def test_verify_payment_of_another_user(
        self,
        mock_zarinpal,
    ):
        other_user = CustomUser.objects.create_user(
            mobile_number="09121111111",
            password="12345678",
            name="Other",
            family="User",
        )

        other_profile = other_user.userprofile

        other_order = Order.objects.create(
            customer=other_profile,
            payment_type=self.payment_type,
            order_state=self.order_state,
            store=self.store,
        )

        payment = Payment.objects.create(
            order=other_order,
            customer=other_profile,
            amount=other_order.get_order_total_price(),
            description="Other payment",
            authority=(
                "A0000000000000000000000000004TEST"
            ),
        )

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse(
                "payments:zarinpal_verify"
            ),
            {
                "Status": "OK",
                "Authority": payment.authority,
            },
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        mock_zarinpal.return_value.verifications.verify.assert_not_called()

    @patch("apps.payments.views.ZarinPal")
    def test_verify_payment_without_data(
        self,
        mock_zarinpal,
    ):
        payment = Payment.objects.create(
            order=self.order,
            customer=self.profile,
            amount=self.order.get_order_total_price(),
            description="Test payment",
            authority=(
                "A0000000000000000000000000005DATA"
            ),
        )

        mock_zarinpal_instance = (
            mock_zarinpal.return_value
        )

        mock_zarinpal_instance.verifications.verify.return_value = {
            "errors": [],
        }

        response = self.client.get(
            reverse(
                "payments:zarinpal_verify"
            ),
            {
                "Status": "OK",
                "Authority": payment.authority,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        payment.refresh_from_db()

        self.assertFalse(
            payment.is_finally
        )

        self.assertIsNone(
            payment.ref_id
        )

    @patch("apps.payments.views.ZarinPal")
    def test_verify_payment_without_status_code(
        self,
        mock_zarinpal,
    ):
        payment = Payment.objects.create(
            order=self.order,
            customer=self.profile,
            amount=self.order.get_order_total_price(),
            description="Test payment",
            authority=(
                "A0000000000000000000000000006CODE"
            ),
        )

        mock_zarinpal_instance = (
            mock_zarinpal.return_value
        )

        mock_zarinpal_instance.verifications.verify.return_value = {
            "data": {},
            "errors": [],
        }

        response = self.client.get(
            reverse(
                "payments:zarinpal_verify"
            ),
            {
                "Status": "OK",
                "Authority": payment.authority,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        payment.refresh_from_db()

        self.assertFalse(
            payment.is_finally
        )

    @patch("apps.payments.views.ZarinPal")
    def test_verify_payment_without_ref_id(
        self,
        mock_zarinpal,
    ):
        payment = Payment.objects.create(
            order=self.order,
            customer=self.profile,
            amount=self.order.get_order_total_price(),
            description="Test payment",
            authority=(
                "A0000000000000000000000000007REF"
            ),
        )

        mock_zarinpal_instance = (
            mock_zarinpal.return_value
        )

        mock_zarinpal_instance.verifications.verify.return_value = {
            "data": {
                "code": 100,
            },
            "errors": [],
        }

        response = self.client.get(
            reverse(
                "payments:zarinpal_verify"
            ),
            {
                "Status": "OK",
                "Authority": payment.authority,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        payment.refresh_from_db()
        self.order.refresh_from_db()

        self.assertFalse(
            payment.is_finally
        )

        self.assertIsNone(
            payment.ref_id
        )

        self.assertFalse(
            self.order.is_finally
        )

    @patch("apps.payments.views.ZarinPal")
    def test_verify_payment_exception(
        self,
        mock_zarinpal,
    ):
        payment = Payment.objects.create(
            order=self.order,
            customer=self.profile,
            amount=self.order.get_order_total_price(),
            description="Test payment",
            authority=(
                "A0000000000000000000000000008ERROR"
            ),
        )

        mock_zarinpal_instance = (
            mock_zarinpal.return_value
        )

        mock_zarinpal_instance.verifications.verify.side_effect = (
            Exception("ZarinPal connection error")
        )

        response = self.client.get(
            reverse(
                "payments:zarinpal_verify"
            ),
            {
                "Status": "OK",
                "Authority": payment.authority,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        payment.refresh_from_db()
        self.order.refresh_from_db()

        self.assertFalse(
            payment.is_finally
        )

        self.assertFalse(
            self.order.is_finally
        )

    @patch("apps.payments.views.ZarinPal")
    def test_verify_uses_payment_amount(
        self,
        mock_zarinpal,
    ):
        payment = Payment.objects.create(
            order=self.order,
            customer=self.profile,
            amount=123456,
            description="Test payment",
            authority=(
                "A0000000000000000000000000009AMOUNT"
            ),
        )

        mock_zarinpal_instance = (
            mock_zarinpal.return_value
        )

        mock_zarinpal_instance.verifications.verify.return_value = {
            "data": {
                "code": 100,
                "ref_id": 999999,
            },
            "errors": [],
        }

        response = self.client.get(
            reverse(
                "payments:zarinpal_verify"
            ),
            {
                "Status": "OK",
                "Authority": payment.authority,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        mock_zarinpal_instance.verifications.verify.assert_called_once_with(
            {
                "amount": 123456,
                "authority": payment.authority,
            }
        )

        payment.refresh_from_db()

        self.assertTrue(
            payment.is_finally
        )

        self.assertEqual(
            payment.ref_id,
            "999999",
        )

    def test_show_verify_message(self):
        session = self.client.session

        session["payment_message"] = "پرداخت موفق بود"
        session.save()

        response = self.client.get(
            reverse(
                "payments:show_verify_message"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "پرداخت موفق بود",
        )

    def test_show_verify_message_without_message(self):
        response = self.client.get(
            reverse(
                "payments:show_verify_message"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "نتیجه‌ای برای پرداخت وجود ندارد.",
        )


