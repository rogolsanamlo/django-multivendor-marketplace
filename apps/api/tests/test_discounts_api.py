from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import CustomUser, Store
from apps.products.models import (
    Product,
    ProductGroup,
    Brand,
    StoreProduct,
)
from apps.discounts.models import (
    Coupon,
    DiscountBasket,
    DiscountBasketDetails,
)


class DiscountAPITests(APITestCase):

    def setUp(self):

        self.user = self.create_user("09120000001")
        self.other_user = self.create_user("09120000002")

        self.store = self.create_store(
            self.user,
            "09121111111",
        )

        self.other_store = self.create_store(
            self.other_user,
            "09122222222",
        )

        now = timezone.now()

        self.coupon = Coupon.objects.create(
            store=self.store,
            coupon_code="TEST10",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=10),
            discount=10,
            is_active=True,
        )

        self.other_coupon = Coupon.objects.create(
            store=self.other_store,
            coupon_code="OTHER10",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=10),
            discount=10,
            is_active=True,
        )

        self.discount_basket = DiscountBasket.objects.create(
            discount_title="Summer Discount",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=10),
            discount=20,
            is_active=True,
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
            is_active=True,
        )

    def test_unauthenticated_user_cannot_see_coupons(self):

        url = reverse("api:coupon-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_unauthenticated_user_cannot_create_coupon(self):

        url = reverse("api:coupon-list")

        response = self.client.post(
            url,
            {
                "coupon_code": "NEW10",
                "start_date": timezone.now(),
                "end_date": timezone.now()
                + timedelta(days=10),
                "discount": 10,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_store_owner_can_see_own_coupons(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse("api:coupon-list")

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
            self.coupon.id,
        )

    def test_store_owner_cannot_see_other_store_coupons(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse("api:coupon-list")

        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        coupon_ids = [
            item["id"]
            for item in response.data
        ]

        self.assertIn(
            self.coupon.id,
            coupon_ids,
        )

        self.assertNotIn(
            self.other_coupon.id,
            coupon_ids,
        )

    def test_store_owner_can_create_coupon(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse("api:coupon-list")

        response = self.client.post(
            url,
            {
                "coupon_code": "NEW20",
                "start_date": timezone.now(),
                "end_date": timezone.now()
                + timedelta(days=10),
                "discount": 20,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        coupon = Coupon.objects.get(
            coupon_code="NEW20"
        )

        self.assertEqual(
            coupon.store,
            self.store,
        )

    def test_user_without_store_cannot_create_coupon(self):

        user = self.create_user(
            "09120000003"
        )

        self.client.force_authenticate(
            user=user
        )

        url = reverse("api:coupon-list")

        response = self.client.post(
            url,
            {
                "coupon_code": "NEW30",
                "start_date": timezone.now(),
                "end_date": timezone.now()
                + timedelta(days=10),
                "discount": 30,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_store_owner_can_see_own_coupon_detail(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:coupon-detail",
            kwargs={
                "pk": self.coupon.id
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.coupon.id,
        )

    def test_store_owner_cannot_see_other_store_coupon_detail(
        self
    ):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:coupon-detail",
            kwargs={
                "pk": self.other_coupon.id
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_store_owner_can_update_own_coupon(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:coupon-detail",
            kwargs={
                "pk": self.coupon.id
            },
        )

        response = self.client.patch(
            url,
            {
                "discount": 25,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.coupon.refresh_from_db()

        self.assertEqual(
            self.coupon.discount,
            25,
        )

    def test_store_owner_cannot_update_other_store_coupon(
        self
    ):

        self.client.force_authenticate(
            user=self.user
        )
        url = reverse(
            "api:coupon-detail",
            kwargs={
                "pk": self.other_coupon.id
            },
        )

        response = self.client.patch(
            url,
            {
                "discount": 50,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.other_coupon.refresh_from_db()

        self.assertEqual(
            self.other_coupon.discount,
            10,
        )

    def test_store_owner_can_delete_own_coupon(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:coupon-detail",
            kwargs={
                "pk": self.coupon.id
            },
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Coupon.objects.filter(
                pk=self.coupon.id
            ).exists()
        )

    def test_store_owner_cannot_delete_other_store_coupon(
        self
    ):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:coupon-detail",
            kwargs={
                "pk": self.other_coupon.id
            },
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            Coupon.objects.filter(
                pk=self.other_coupon.id
            ).exists()
        )

    def test_authenticated_user_can_see_active_discount_baskets(
        self
    ):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:discount-basket-list"
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
            self.discount_basket.id,
        )

    def test_unauthenticated_user_cannot_see_discount_baskets(
        self
    ):

        url = reverse(
            "api:discount-basket-list"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_see_discount_basket_detail(
        self
    ):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:discount-basket-detail",
            kwargs={
                "pk": self.discount_basket.id
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.discount_basket.id,
        )

    def test_discount_basket_api_is_read_only(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:discount-basket-list"
        )

        response = self.client.post(
            url,
            {
                "discount_title": "Hack",
                "discount": 99,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_authenticated_user_can_see_discount_basket_details(
        self
    ):

        brand = Brand.objects.create(
            brand_title="Test Brand"
        )

        product_group = ProductGroup.objects.create(
            group_title="Test Group"
        )

        product = Product.objects.create(
            product_name="Test Product",
            brand=brand,
            slug="test-product",
            is_active=True,
        )

        product.product_group.add(
            product_group
        )

        store_product = StoreProduct.objects.create(
            store=self.store,
            product=product,
            price=100000,
            is_active=True,
        )

        detail = DiscountBasketDetails.objects.create(
            discount_basket=self.discount_basket,
            store_product=store_product,
        )

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:discount-basket-details-list"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        detail_ids = [
            item["id"]
            for item in response.data
        ]

        self.assertIn(
            detail.id,
            detail_ids,
        )
