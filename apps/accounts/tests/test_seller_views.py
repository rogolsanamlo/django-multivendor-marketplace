from django.conf import settings
from django.shortcuts import resolve_url
from django.urls import reverse

from apps.accounts.models import CustomUser, Store
from apps.orders.models import Order, OrderDetails
from apps.products.models import Brand, Product, ProductGroup, StoreProduct
from apps.tests.base import BaseAccountTest
from apps.warehouses.models import Warehouse, WarehouseType


class BaseSellerTest(BaseAccountTest):

    def setUp(self):
        super().setUp()

        self.activate_user()
        self.client.force_login(self.user)

        self.brand = Brand.objects.create(brand_title="Samsung")

        self.group = ProductGroup.objects.create(
            group_title="Mobile",
            slug="mobile",
        )

        self.product = Product.objects.create(
            product_name="Galaxy A56",
            brand=self.brand,
            slug="galaxy-a56",
        )

        self.product.product_group.add(self.group)

        self.other_product = Product.objects.create(
            product_name="Galaxy S24",
            brand=self.brand,
            slug="galaxy-s24",
        )

        self.other_product.product_group.add(self.group)

    def create_other_store(self):
        other_user = CustomUser.objects.create_user(
            mobile_number="09128888888",
            password="123456",
        )

        return Store.objects.create(
            user=other_user,
            store_name="Other Shop",
            store_phone="09122222222",
        )


class SellerAccessTests(BaseSellerTest):

    URL_NAMES = [
        "accounts:seller_products",
        "accounts:seller_product_add",
        "accounts:seller_orders",
        "accounts:seller_stock",
    ]

    def test_anonymous_user_is_redirected_to_login(self):
        self.client.logout()

        for name in self.URL_NAMES:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))

                self.assertEqual(response.status_code, 302)
                self.assertIn(
                    resolve_url(settings.LOGIN_URL),
                    response["Location"],
                )

    def test_user_without_store_is_redirected_to_create_store(self):
        user = CustomUser.objects.create_user(
            mobile_number="09127777777",
            password="123456",
        )
        user.is_active = True
        user.save()

        self.client.force_login(user)

        for name in self.URL_NAMES:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))

                self.assertRedirects(
                    response,
                    reverse("accounts:create_store"),
                    fetch_redirect_response=False,
                )

    def test_anonymous_post_does_not_change_stock(self):
        store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=100000,
        )

        self.client.logout()

        self.client.post(
            reverse("accounts:seller_stock"),
            data={
                "store_product": store_product.id,
                "movement": "input",
                "qty": 5,
            },
        )

        self.assertFalse(Warehouse.objects.exists())


class SellerProductsTests(BaseSellerTest):

    def test_list_shows_only_own_products(self):
        StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=100000,
        )

        StoreProduct.objects.create(
            store=self.create_other_store(),
            product=self.other_product,
            price=200000,
        )

        response = self.client.get(reverse("accounts:seller_products"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Galaxy A56")
        self.assertNotContains(response, "Galaxy S24")

    def test_add_page_loads(self):
        response = self.client.get(reverse("accounts:seller_product_add"))

        self.assertEqual(response.status_code, 200)

    def test_add_product_to_store(self):
        response = self.client.post(
            reverse("accounts:seller_product_add"),
            data={
                "product": self.product.id,
                "price": 150000,
                "is_active": "on",
            },
        )

        self.assertRedirects(
            response,
            reverse("accounts:seller_products"),
            fetch_redirect_response=False,
        )

        store_product = StoreProduct.objects.get(
            store=self.store,
            product=self.product,
        )

        self.assertEqual(store_product.price, 150000)
        self.assertTrue(store_product.is_active)

    def test_unchecked_is_active_saves_false(self):
        self.client.post(
            reverse("accounts:seller_product_add"),
            data={
                "product": self.product.id,
                "price": 150000,
            },
        )

        store_product = StoreProduct.objects.get(
            store=self.store,
            product=self.product,
        )

        self.assertFalse(store_product.is_active)

    def test_listed_product_is_not_offered_again(self):
        StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=100000,
        )

        response = self.client.post(
            reverse("accounts:seller_product_add"),
            data={
                "product": self.product.id,
                "price": 150000,
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            StoreProduct.objects.filter(store=self.store).count(),
            1,
        )

    def test_inactive_catalog_product_is_not_offered(self):
        self.other_product.is_active = False
        self.other_product.save()

        response = self.client.post(
            reverse("accounts:seller_product_add"),
            data={
                "product": self.other_product.id,
                "price": 150000,
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            StoreProduct.objects.filter(store=self.store).exists()
        )

    def test_price_must_be_positive(self):
        response = self.client.post(
            reverse("accounts:seller_product_add"),
            data={
                "product": self.product.id,
                "price": 0,
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            StoreProduct.objects.filter(store=self.store).exists()
        )

    def test_edit_page_loads(self):
        store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=100000,
        )

        response = self.client.get(
            reverse(
                "accounts:seller_product_edit",
                args=[store_product.id],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_edit_price(self):
        store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=100000,
        )

        response = self.client.post(
            reverse(
                "accounts:seller_product_edit",
                args=[store_product.id],
            ),
            data={
                "price": 120000,
                "is_active": "on",
            },
        )

        self.assertRedirects(
            response,
            reverse("accounts:seller_products"),
            fetch_redirect_response=False,
        )

        store_product.refresh_from_db()

        self.assertEqual(store_product.price, 120000)

    def test_edit_cannot_change_the_product(self):
        store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=100000,
        )

        self.client.post(
            reverse(
                "accounts:seller_product_edit",
                args=[store_product.id],
            ),
            data={
                "product": self.other_product.id,
                "price": 120000,
                "is_active": "on",
            },
        )

        store_product.refresh_from_db()

        self.assertEqual(store_product.product, self.product)

    def test_cannot_edit_another_stores_product(self):
        other_product = StoreProduct.objects.create(
            store=self.create_other_store(),
            product=self.other_product,
            price=200000,
        )

        response = self.client.get(
            reverse(
                "accounts:seller_product_edit",
                args=[other_product.id],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_cannot_post_edit_another_stores_product(self):
        other_store_product = StoreProduct.objects.create(
            store=self.create_other_store(),
            product=self.other_product,
            price=200000,
        )

        response = self.client.post(
            reverse(
                "accounts:seller_product_edit",
                args=[other_store_product.id],
            ),
            data={
                "price": 1,
                "is_active": "on",
            },
        )

        self.assertEqual(response.status_code, 404)

        other_store_product.refresh_from_db()

        self.assertEqual(other_store_product.price, 200000)


class SellerOrdersTests(BaseSellerTest):

    def test_shows_only_finalized_orders_of_own_store(self):
        store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=100000,
        )

        finalized = Order.objects.create(
            customer=self.profile,
            store=self.store,
            is_finally=True,
        )

        OrderDetails.objects.create(
            order=finalized,
            store_product=store_product,
            qty=2,
            price=100000,
        )

        Order.objects.create(
            customer=self.profile,
            store=self.store,
            is_finally=False,
        )

        Order.objects.create(
            customer=self.profile,
            store=self.create_other_store(),
            is_finally=True,
        )

        response = self.client.get(reverse("accounts:seller_orders"))

        self.assertEqual(response.status_code, 200)

        orders = response.context["orders"]

        self.assertEqual([o.id for o in orders], [finalized.id])
        self.assertEqual(orders[0].items_total, 200000)
        self.assertContains(response, "Galaxy A56")

    def test_no_orders_shows_empty_list(self):
        response = self.client.get(reverse("accounts:seller_orders"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["orders"]), [])


class SellerStockTests(BaseSellerTest):

    def setUp(self):
        super().setUp()

        self.store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=100000,
        )

    def test_stock_page_loads(self):
        response = self.client.get(reverse("accounts:seller_stock"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Galaxy A56")

    def test_stock_page_hides_other_stores_products(self):
        StoreProduct.objects.create(
            store=self.create_other_store(),
            product=self.other_product,
            price=200000,
        )

        response = self.client.get(reverse("accounts:seller_stock"))

        self.assertNotContains(response, "Galaxy S24")

    def test_input_increases_stock(self):
        response = self.client.post(
            reverse("accounts:seller_stock"),
            data={
                "store_product": self.store_product.id,
                "movement": "input",
                "qty": 5,
            },
        )

        self.assertRedirects(
            response,
            reverse("accounts:seller_stock"),
            fetch_redirect_response=False,
        )

        self.assertEqual(self.store_product.get_number_in_warehouse(), 5)

        self.assertTrue(
            WarehouseType.objects.filter(code="input").exists()
        )

    def test_output_decreases_stock(self):
        self.client.post(
            reverse("accounts:seller_stock"),
            data={
                "store_product": self.store_product.id,
                "movement": "input",
                "qty": 5,
            },
        )

        self.client.post(
            reverse("accounts:seller_stock"),
            data={
                "store_product": self.store_product.id,
                "movement": "output",
                "qty": 2,
            },
        )

        self.assertEqual(self.store_product.get_number_in_warehouse(), 3)

    def test_output_more_than_stock_is_rejected(self):
        response = self.client.post(
            reverse("accounts:seller_stock"),
            data={
                "store_product": self.store_product.id,
                "movement": "output",
                "qty": 1,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Warehouse.objects.exists())

    def test_output_equal_to_stock_is_allowed(self):
        self.client.post(
            reverse("accounts:seller_stock"),
            data={
                "store_product": self.store_product.id,
                "movement": "input",
                "qty": 5,
            },
        )

        response = self.client.post(
            reverse("accounts:seller_stock"),
            data={
                "store_product": self.store_product.id,
                "movement": "output",
                "qty": 5,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.store_product.get_number_in_warehouse(), 0)

    def test_output_one_more_than_stock_is_rejected(self):
        self.client.post(
            reverse("accounts:seller_stock"),
            data={
                "store_product": self.store_product.id,
                "movement": "input",
                "qty": 5,
            },
        )

        response = self.client.post(
            reverse("accounts:seller_stock"),
            data={
                "store_product": self.store_product.id,
                "movement": "output",
                "qty": 6,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.store_product.get_number_in_warehouse(), 5)
        self.assertEqual(Warehouse.objects.count(), 1)

    def test_qty_must_be_at_least_one(self):
        response = self.client.post(
            reverse("accounts:seller_stock"),
            data={
                "store_product": self.store_product.id,
                "movement": "input",
                "qty": 0,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Warehouse.objects.exists())

    def test_invalid_movement_is_rejected(self):
        response = self.client.post(
            reverse("accounts:seller_stock"),
            data={
                "store_product": self.store_product.id,
                "movement": "other",
                "qty": 5,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Warehouse.objects.exists())

    def test_price_and_registering_user_are_saved(self):
        self.client.post(
            reverse("accounts:seller_stock"),
            data={
                "store_product": self.store_product.id,
                "movement": "input",
                "qty": 5,
                "price": 5000,
            },
        )

        entry = Warehouse.objects.get()

        self.assertEqual(entry.price, 5000)
        self.assertEqual(entry.user_registered, self.user)

    def test_cannot_change_stock_of_another_stores_product(self):
        other_product = StoreProduct.objects.create(
            store=self.create_other_store(),
            product=self.other_product,
            price=200000,
        )

        response = self.client.post(
            reverse("accounts:seller_stock"),
            data={
                "store_product": other_product.id,
                "movement": "input",
                "qty": 5,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Warehouse.objects.exists())
