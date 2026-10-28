from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import (
    CustomUser,
    Store,
)
from apps.orders.models import (
    Order,
    OrderDetails,
    OrderState,
    PaymentType,
)
from apps.orders.shop_cart import ShopCart
from apps.products.models import (
    Brand,
    Product,
    ProductGroup,
    StoreProduct,
)


class BaseOrderViewTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            mobile_number="09120000000",
            password="12345678",
            name="Ali",
            family="Ahmadi",
            email="ali@test.com",
        )

        self.profile = self.user.userprofile
        self.profile.address = "Tehran"
        self.profile.save()

        self.user.is_active = True
        self.user.save()

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

        OrderDetails.objects.create(
            order=self.order,
            store_product=self.store_product,
            qty=2,
            price=100000,
        )

        self.client.login(
            mobile_number="09120000000",
            password="12345678",
        )

        session = self.client.session

        request = type(
            "Request",
            (),
            {"session": session},
        )()

        cart = ShopCart(request)

        cart.add_to_shop_cart(
            self.store_product,
            2,
        )

        session.save()


class ShopCartViewsTests(BaseOrderViewTest):

    def test_shop_cart_view(self):
        response = self.client.get(
            reverse("orders:shop_cart")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_show_shop_cart(self):
        response = self.client.get(
            reverse("orders:show_shop_cart")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_status_shop_cart(self):
        response = self.client.get(
            reverse("orders:status_of_shop_cart")
        )

        self.assertEqual(
            response.status_code,
            200,
        )


class CreateOrderViewTests(BaseOrderViewTest):

    def test_create_order(self):
        initial_count = Order.objects.count()

        response = self.client.get(
            reverse("orders:create_order")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            Order.objects.count(),
            initial_count + 1,
        )

        order = Order.objects.latest("id")

        self.assertEqual(
            order.customer,
            self.profile,
        )

        self.assertEqual(
            order.store,
            self.store,
        )

        self.assertEqual(
            order.payment_type,
            self.payment_type,
        )

        self.assertEqual(
            order.details.count(),
            1,
        )


class CheckoutOrderViewTests(BaseOrderViewTest):

    def test_checkout_get(self):
        response = self.client.get(
            reverse(
                "orders:checkout_order",
                args=[self.order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_checkout_post(self):
        response = self.client.post(
            reverse(
                "orders:checkout_order",
                args=[self.order.id],
            ),
            {
                "name": "Reza",
                "family": "Mohammadi",
                "email": "reza@test.com",
                "phone_number": "09121111111",
                "address": "Tabriz",
                "description": "test order",
                "payment_type": self.payment_type.id,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertRedirects(
            response,
            reverse(
                "payments:zarinpal_payment",
                args=[self.order.id],
            ),
            fetch_redirect_response=False,
        )

        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(
            self.user.name,
            "Reza",
        )

        self.assertEqual(
            self.user.family,
            "Mohammadi",
        )

        self.assertEqual(
            self.user.email,
            "reza@test.com",
        )

        self.assertEqual(
            self.user.mobile_number,
            "09121111111",
        )

        self.assertEqual(
            self.profile.address,
            "Tabriz",
        )

        self.assertEqual(
            self.order.description,
            "test order",
        )

        self.assertEqual(
            self.order.payment_type,
            self.payment_type,
        )


class OrderRegressionTests(BaseOrderViewTest):

    def test_add_to_shop_cart_stores_json_serializable_prices(self):
        response = self.client.get(
            reverse("orders:add_to_shop_cart"),
            {
                "product_id": self.store_product.id,
                "qty": 1,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        cart = self.client.session["shop_cart"]

        item = cart[str(self.store_product.id)]

        self.assertIsInstance(item["price"], int)
        self.assertIsInstance(item["final_price"], int)

    def test_add_to_shop_cart_invalid_qty(self):
        response = self.client.get(
            reverse("orders:add_to_shop_cart"),
            {
                "product_id": self.store_product.id,
                "qty": 0,
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_create_order_with_empty_cart_creates_nothing(self):
        session = self.client.session
        session["shop_cart"] = {}
        session.save()

        initial_count = Order.objects.count()

        response = self.client.get(
            reverse("orders:create_order")
        )

        self.assertRedirects(
            response,
            reverse("orders:shop_cart"),
            fetch_redirect_response=False,
        )

        self.assertEqual(
            Order.objects.count(),
            initial_count,
        )

    def test_checkout_of_another_users_order_is_404(self):
        other_user = CustomUser.objects.create_user(
            mobile_number="09129999999",
            password="12345678",
        )

        other_order = Order.objects.create(
            customer=other_user.userprofile,
            store=self.store,
            payment_type=self.payment_type,
        )

        response = self.client.get(
            reverse(
                "orders:checkout_order",
                args=[other_order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_checkout_post_with_missing_address_shows_errors(self):
        response = self.client.post(
            reverse(
                "orders:checkout_order",
                args=[self.order.id],
            ),
            {
                "name": "Reza",
                "family": "Mohammadi",
                "email": "",
                "phone_number": "",
                "address": "",
                "description": "",
                "payment_type": self.payment_type.id,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "این فیلد نمی تواند خالی باشد")

        self.profile.refresh_from_db()

        self.assertEqual(self.profile.address, "Tehran")

    def test_checkout_submit_button_belongs_to_the_form(self):
        response = self.client.get(
            reverse(
                "orders:checkout_order",
                args=[self.order.id],
            )
        )

        self.assertContains(response, 'id="checkout-form"')
        self.assertContains(response, 'form="checkout-form"')

    def test_invalid_coupon_shows_an_error(self):
        response = self.client.post(
            reverse(
                "orders:applay_coupon",
                args=[self.order.id],
            ),
            {"coupon_code": "WRONG"},
            follow=True,
        )

        self.assertContains(response, "کد وارد شده معتبر نیست")

    def test_checkout_page_shows_the_payment_method_heading(self):
        response = self.client.get(
            reverse(
                "orders:checkout_order",
                args=[self.order.id],
            )
        )

        self.assertContains(response, "روش پرداخت")

    def test_default_payment_type_has_a_persian_title(self):
        PaymentType.objects.all().delete()

        self.client.get(
            reverse("orders:add_to_shop_cart"),
            {
                "product_id": self.store_product.id,
                "qty": 1,
            },
        )

        self.client.get(reverse("orders:create_order"))

        self.assertEqual(
            PaymentType.objects.get().payment_title,
            "پرداخت آنلاین",
        )
