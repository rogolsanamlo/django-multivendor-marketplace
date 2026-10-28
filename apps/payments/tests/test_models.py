from apps.orders.tests.test_models import BaseOrderTest
from apps.payments.models import Payment


class PaymentTests(BaseOrderTest):

    def setUp(self):
        super().setUp()

        self.payment = Payment.objects.create(
            order=self.order,
            customer=self.profile,
            amount=self.order.get_order_total_price(),
            description="پرداخت از طریق درگاه زرین پال",
        )

    def test_payment_created(self):
        self.assertIsNotNone(
            self.payment.id
        )

        self.assertEqual(
            Payment.objects.count(),
            1,
        )

    def test_payment_default_is_finally(self):
        self.assertFalse(
            self.payment.is_finally
        )

    def test_payment_authority_is_empty_initially(self):
        self.assertIsNone(
            self.payment.authority
        )

    def test_payment_authority_can_be_saved(self):
        self.payment.authority = (
            "A0000000000000000000000000000TEST"
        )

        self.payment.save()
        self.payment.refresh_from_db()

        self.assertEqual(
            self.payment.authority,
            "A0000000000000000000000000000TEST",
        )

    def test_payment_gateway_fields_are_empty_initially(self):
        self.assertIsNone(
            self.payment.status_code
        )

        self.assertIsNone(
            self.payment.ref_id
        )

    def test_payment_gateway_result_can_be_saved(self):
        self.payment.status_code = 100
        self.payment.ref_id = "123456789"

        self.payment.save()
        self.payment.refresh_from_db()

        self.assertEqual(
            self.payment.status_code,
            100,
        )

        self.assertEqual(
            self.payment.ref_id,
            "123456789",
        )