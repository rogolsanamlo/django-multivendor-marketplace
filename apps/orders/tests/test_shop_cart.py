from django.test import Client, TestCase

from apps.accounts.models import (
    CustomUser,
    Store,
)
from apps.orders.shop_cart import ShopCart
from apps.products.models import (
    Brand,
    Product,
    ProductGroup,
    StoreProduct,
)


class ShopCartTests(TestCase):

    def setUp(self):
        self.client = Client()

        session = self.client.session
        session.save()

        self.user = CustomUser.objects.create_user(
            mobile_number="09120000000",
            password="12345678",
            name="Ali",
            family="Ahmadi",
        )

        self.store = Store.objects.create(
            user=self.user,
            store_name="Store 1",
            store_phone="09121111111",
        )

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

        self.cart = ShopCart(
            self.client.request().wsgi_request
        )

    def test_create_shop_cart(self):
        self.assertIn(
            "shop_cart",
            self.cart.session,
        )

    def test_add_to_shop_cart(self):
        result = self.cart.add_to_shop_cart(
            self.store_product,
            1,
        )

        self.assertTrue(
            result
        )

        self.assertEqual(
            self.cart.shop_cart[
                str(self.store_product.id)
            ]["qty"],
            1,
        )

    def test_add_same_product(self):
        self.cart.add_to_shop_cart(
            self.store_product,
            1,
        )

        self.cart.add_to_shop_cart(
            self.store_product,
            1,
        )

        self.assertEqual(
            self.cart.shop_cart[
                str(self.store_product.id)
            ]["qty"],
            2,
        )

    def test_delete_from_shop_cart(self):
        self.cart.add_to_shop_cart(
            self.store_product,
            1,
        )

        self.cart.delete_from_shop_cart(
            self.store_product
        )

        self.assertEqual(
            len(self.cart.shop_cart),
            0,
        )

    def test_update(self):
        self.cart.add_to_shop_cart(
            self.store_product,
            1,
        )

        self.cart.update(
            [str(self.store_product.id)],
            [5],
        )

        self.assertEqual(
            self.cart.shop_cart[
                str(self.store_product.id)
            ]["qty"],
            5,
        )

    def test_calc_total_price(self):
        self.cart.add_to_shop_cart(
            self.store_product,
            2,
        )

        expected = (
            self.cart.shop_cart[
                str(self.store_product.id)
            ]["final_price"]
            * 2
        )

        self.assertEqual(
            self.cart.calc_total_price(),
            expected,
        )

    def test_cannot_add_product_from_another_store(self):
        user2 = CustomUser.objects.create_user(
            mobile_number="09120000001",
            password="12345678",
            name="Reza",
            family="Karimi",
        )

        store2 = Store.objects.create(
            user=user2,
            store_name="Store 2",
            store_phone="09122222222",
        )

        product2 = Product.objects.create(
            product_name="Galaxy S25",
            brand=self.brand,
            slug="galaxy-s25",
        )

        product2.product_group.add(
            self.group
        )

        store_product2 = StoreProduct.objects.create(
            store=store2,
            product=product2,
            price=200000,
        )

        self.cart.add_to_shop_cart(
            self.store_product,
            1,
        )

        result = self.cart.add_to_shop_cart(
            store_product2,
            1,
        )

        self.assertFalse(
            result
        )

    def test_iter(self):
        self.cart.add_to_shop_cart(
            self.store_product,
            2,
        )

        items = list(
            self.cart
        )

        self.assertEqual(
            len(items),
            1,
        )

        self.assertIn(
            "store_product",
            items[0],
        )

        self.assertIn(
            "qty",
            items[0],
        )

        self.assertIn(
            "final_price",
            items[0],
        )

        self.assertIn(
            "total_price",
            items[0],
        )