from unittest.mock import patch

from django.urls import reverse

from apps.orders.tests.test_models import BaseOrderTest
from apps.payments.models import Payment
from apps.warehouses.models import Warehouse, WarehouseType


class StockDecreaseAfterPaymentTests(BaseOrderTest):
    """Paying an order takes its items out of the store's stock (once)."""

    AUTHORITY = "A0000000000000000000000000000STOCK"

    def setUp(self):
        super().setUp()

        self.user.is_active = True
        self.user.save()
        self.client.force_login(self.user)

        input_type = WarehouseType.objects.create(
            warehouse_type_title="ورود به انبار",
            code=WarehouseType.INPUT,
        )

        Warehouse.objects.create(
            warehouse_type=input_type,
            user_registered=self.user,
            store_product=self.store_product,
            qty=10,
        )

        self.payment = Payment.objects.create(
            order=self.order,
            customer=self.profile,
            amount=self.order.get_order_total_price(),
            authority=self.AUTHORITY,
        )

    def verify(self, mock_zarinpal, code):
        mock_zarinpal.return_value.verifications.verify.return_value = {
            "data": {"code": code, "ref_id": 111},
            "errors": [],
        }

        return self.client.get(
            reverse("payments:zarinpal_verify"),
            {"Status": "OK", "Authority": self.AUTHORITY},
        )

    @patch("apps.payments.views.ZarinPal")
    def test_successful_payment_decreases_stock(self, mock_zarinpal):
        self.assertEqual(self.store_product.get_number_in_warehouse(), 10)

        self.verify(mock_zarinpal, 100)

        # The order has one line with qty=2.
        self.assertEqual(self.store_product.get_number_in_warehouse(), 8)

    @patch("apps.payments.views.ZarinPal")
    def test_repeated_callback_does_not_decrease_twice(self, mock_zarinpal):
        self.verify(mock_zarinpal, 100)
        self.verify(mock_zarinpal, 101)
        self.verify(mock_zarinpal, 101)

        self.assertEqual(self.store_product.get_number_in_warehouse(), 8)

    @patch("apps.payments.views.ZarinPal")
    def test_code_101_on_unfinished_order_decreases_once(self, mock_zarinpal):
        # E.g. the first callback crashed after the gateway verified.
        self.verify(mock_zarinpal, 101)
        self.verify(mock_zarinpal, 101)

        self.order.refresh_from_db()
        self.assertTrue(self.order.is_finally)
        self.assertEqual(self.store_product.get_number_in_warehouse(), 8)

    @patch("apps.payments.views.ZarinPal")
    def test_failed_payment_leaves_stock_unchanged(self, mock_zarinpal):
        self.verify(mock_zarinpal, -50)

        self.order.refresh_from_db()
        self.assertFalse(self.order.is_finally)
        self.assertEqual(self.store_product.get_number_in_warehouse(), 10)

    def test_cancelled_payment_leaves_stock_unchanged(self):
        self.client.get(
            reverse("payments:zarinpal_verify"),
            {"Status": "NOK", "Authority": self.AUTHORITY},
        )

        self.assertEqual(self.store_product.get_number_in_warehouse(), 10)

    @patch("apps.payments.views.ZarinPal")
    def test_output_rows_do_not_change_purchase_cost(self, mock_zarinpal):
        """get_store_profit sums only input rows, so it must be unaffected."""
        from apps.analytics.services import get_store_profit

        before = get_store_profit(self.store)["buy"]
        self.verify(mock_zarinpal, 100)

        self.assertEqual(get_store_profit(self.store)["buy"], before)
