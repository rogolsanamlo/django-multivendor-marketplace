from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

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
from apps.products.models import (
    Brand,
    Product,
    ProductGroup,
    StoreProduct,
)


class OrdersAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = CustomUser.objects.create_user(
            mobile_number="09120000000",
            password="123456",
            name="Ali",
            family="Ahmadi",
        )

        self.other_user = CustomUser.objects.create_user(
            mobile_number="09123333333",
            password="123456",
            name="Reza",
            family="Rezaei",
        )

        self.profile = self.user.userprofile
        self.other_profile = self.other_user.userprofile

        self.store = Store.objects.create(
            user=self.user,
            store_name="Digital Shop",
            store_phone="09121111111",
            is_active=True,
        )

        self.other_store = Store.objects.create(
            user=self.other_user,
            store_name="Other Shop",
            store_phone="09122222222",
            is_active=True,
        )

        self.brand = Brand.objects.create(
            brand_title="Samsung",
        )

        self.product_group = ProductGroup.objects.create(
            group_title="Mobile",
            slug="mobile",
        )

        self.product = Product.objects.create(
            product_name="Galaxy S25",
            brand=self.brand,
            slug="galaxy-s25",
        )

        self.product.product_group.add(
            self.product_group
        )

        self.store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=50000000,
        )

        self.payment_type = PaymentType.objects.create(
            payment_title="Online",
        )

        self.order_state = OrderState.objects.create(
            order_state_title="Pending",
        )

        self.order = Order.objects.create(
            customer=self.profile,
            store=self.store,
            payment_type=self.payment_type,
            order_state=self.order_state,
            is_finally=True,
        )

        self.order_detail = OrderDetails.objects.create(
            order=self.order,
            store_product=self.store_product,
            qty=2,
            price=50000000,
        )

        self.other_store_product = StoreProduct.objects.create(
            store=self.other_store,
            product=self.product,
            price=60000000,
        )

        self.other_order = Order.objects.create(
            customer=self.other_profile,
            store=self.other_store,
            payment_type=self.payment_type,
            order_state=self.order_state,
            is_finally=True,
        )

        self.other_order_detail = OrderDetails.objects.create(
            order=self.other_order,
            store_product=self.other_store_product,
            qty=1,
            price=60000000,
        )

    def test_unauthenticated_user_cannot_access_orders(self):
        url = reverse("api:order-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_can_see_own_orders(self):
        self.client.force_authenticate(
            user=self.user
        )

        url = reverse("api:order-list")

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
            self.order.id,
        )

    def test_user_can_see_own_order_detail(self):
        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:order-detail",
            kwargs={
                "pk": self.order.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.order.id,
        )

    def test_user_cannot_see_other_user_order(self):
        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:order-detail",
            kwargs={
                "pk": self.other_order.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_unauthenticated_user_cannot_access_store_orders(self):
        url = reverse(
            "api:store-order-list"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_store_owner_can_see_store_orders(self):
        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:store-order-list"
        )

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
            self.order.id,
        )

    def test_store_owner_can_see_store_order_detail(self):
        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:store-order-detail",
            kwargs={
                "pk": self.order.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.order.id,
        )

    def test_store_owner_cannot_see_other_store_order(self):
        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:store-order-detail",
            kwargs={
                "pk": self.other_order.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_user_without_store_cannot_access_store_orders(self):
        user_without_store = CustomUser.objects.create_user(
            mobile_number="09124444444",
            password="123456",
            name="Test",
            family="User",
        )

        self.client.force_authenticate(
            user=user_without_store
        )

        url = reverse(
            "api:store-order-list"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_inactive_store_owner_cannot_access_store_orders(self):
        self.store.is_active = False
        self.store.save()

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:store-order-list"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_authenticated_user_can_see_payment_types(self):
        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:payment-type-list"
        )

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
            response.data[0]["payment_title"],
            "Online",
        )

    def test_authenticated_user_can_see_order_states(self):
        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:order-state-list"
        )

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
            response.data[0]["order_state_title"],
            "Pending",
        )