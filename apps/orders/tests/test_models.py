import utils

from apps.orders.models import (
    Order,
    OrderDetails,
    OrderState,
    PaymentType,
)
from apps.products.models import (
    Brand,
    Product,
    ProductGroup,
    StoreProduct,
)
from apps.tests.base import BaseAccountTest


class BaseOrderTest(BaseAccountTest):

    def setUp(self):
        super().setUp()

        self.store = self.user.store
        self.store.store_phone = "09121111111"
        self.store.save()

        self.profile.address = "Tehran"
        self.profile.save()

        self.brand = Brand.objects.create(
            brand_title="Samsung",
        )

        self.group = ProductGroup.objects.create(
            group_title="Mobile",
            slug="mobile",
        )

        self.product = Product.objects.create(
            product_name="Galaxy A56",
            brand=self.brand,
            slug="galaxy-a56",
        )

        self.product.product_group.add(
            self.group
        )

        self.store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=100000,
        )

        self.payment_type = PaymentType.objects.create(
            payment_title="Online",
        )

        self.order_state = OrderState.objects.create(
            order_state_title="Pending",
        )

        self.order = Order.objects.create(
            customer=self.profile,
            payment_type=self.payment_type,
            order_state=self.order_state,
            store=self.store,
        )

        self.detail = OrderDetails.objects.create(
            order=self.order,
            store_product=self.store_product,
            qty=2,
            price=100000,
        )


class PaymentTypeTests(BaseOrderTest):

    def test_str(self):
        self.assertEqual(
            str(self.payment_type),
            "Online",
        )


class OrderStateTests(BaseOrderTest):

    def test_str(self):
        self.assertEqual(
            str(self.order_state),
            "Pending",
        )


class OrderTests(BaseOrderTest):

    def test_str(self):
        self.assertEqual(
            str(self.order),
            f"{self.profile}\t{self.order.id}\tFalse",
        )

    def test_order_code_created(self):
        self.assertIsNotNone(
            self.order.order_code,
        )

    def test_default_is_finally(self):
        self.assertFalse(
            self.order.is_finally,
        )

    def test_default_discount(self):
        self.assertEqual(
            self.order.discount,
            0,
        )

    def test_get_order_total_price(self):
        total = (
            self.detail.price
            * self.detail.qty
        )

        final_price, delivery, tax = (
            utils.price_by_delivery_tax(
                total,
                self.order.discount,
            )
        )

        self.assertEqual(
            self.order.get_order_total_price(),
            int(final_price * 10),
        )


class OrderDetailsTests(BaseOrderTest):

    def test_str(self):
        self.assertEqual(
            str(self.detail),
            f"{self.order}\t{self.store_product}\t2\t100000",
        )

    def test_order_relation(self):
        self.assertEqual(
            self.detail.order,
            self.order,
        )

    def test_store_product_relation(self):
        self.assertEqual(
            self.detail.store_product,
            self.store_product,
        )

    def test_default_qty(self):
        detail = OrderDetails.objects.create(
            order=self.order,
            store_product=self.store_product,
            price=50000,
        )

        self.assertEqual(
            detail.qty,
            1,
        )

    def test_price(self):
        self.assertEqual(
            self.detail.price,
            100000,
        )