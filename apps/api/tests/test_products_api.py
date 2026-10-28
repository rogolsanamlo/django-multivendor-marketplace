from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import (
    CustomUser,
    Store,
)
from apps.products.models import (
    Brand,
    Product,
    ProductGroup,
    StoreProduct,
)


class ProductAPITest(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            mobile_number="09120000001",
            email="test@example.com",
            name="Test",
            family="User",
            password="test123"
        )

        self.brand = Brand.objects.create(
            brand_title="Apple",
            slug="apple"
        )

        self.product_group = ProductGroup.objects.create(
            group_title="Mobile",
            slug="mobile"
        )

        self.product = Product.objects.create(
            product_name="iPhone 15",
            brand=self.brand,
            slug="iphone-15",
            image_name="products/test.jpg",
            is_active=True
        )

        self.product.product_group.add(
            self.product_group
        )

        self.list_url = reverse(
            "api:product-list"
        )

        self.detail_url = reverse(
            "api:product-detail",
            kwargs={
                "pk": self.product.pk
            }
        )

    def test_product_list_returns_active_products(self):
        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

    def test_product_detail_returns_active_product(self):
        response = self.client.get(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["id"],
            self.product.id
        )

    def test_inactive_product_is_not_in_list(self):
        self.product.is_active = False
        self.product.save()

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            0
        )

    def test_inactive_product_detail_returns_404(self):
        self.product.is_active = False
        self.product.save()

        response = self.client.get(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )


class StoreProductAPITest(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            mobile_number="09120000002",
            email="store@example.com",
            name="Store",
            family="Owner",
            password="test123"
        )

        self.brand = Brand.objects.create(
            brand_title="Apple",
            slug="apple"
        )

        self.product_group = ProductGroup.objects.create(
            group_title="Mobile",
            slug="mobile"
        )

        self.product = Product.objects.create(
            product_name="iPhone 15",
            brand=self.brand,
            slug="iphone-15",
            image_name="products/test.jpg",
            is_active=True
        )

        self.product.product_group.add(
            self.product_group
        )

        self.store = Store.objects.create(
            user=self.user,
            store_name="Test Store",
            store_phone="09120000003",
            slug="test-store",
            is_active=True
        )

        self.store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=50000000,
            is_active=True
        )

        self.list_url = reverse(
            "api:store-product-list"
        )

        self.detail_url = reverse(
            "api:store-product-detail",
            kwargs={
                "pk": self.store_product.pk
            }
        )

    def test_store_product_list_returns_active_products(self):
        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

    def test_store_product_detail_returns_product(self):
        response = self.client.get(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["id"],
            self.store_product.id
        )

    def test_inactive_store_product_is_not_in_list(self):
        self.store_product.is_active = False
        self.store_product.save()

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            0
        )

    def test_inactive_store_product_detail_returns_404(self):
        self.store_product.is_active = False
        self.store_product.save()

        response = self.client.get(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_store_product_price_is_returned(self):
        response = self.client.get(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            str(response.data["price"]),
            "50000000.00"
        )


    def test_store_owner_can_create_store_product(self):
        another_product = Product.objects.create(
            product_name="iPhone 16",
            brand=self.brand,
            slug="iphone-16",
            image_name="products/test2.jpg",
            is_active=True,
        )

        another_product.product_group.add(
            self.product_group
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.list_url,
            {
                "product": another_product.id,
                "price": "60000000.00",
                "is_active": True,
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        store_product = StoreProduct.objects.get(
            store=self.store,
            product=another_product
        )

        self.assertEqual(
            store_product.price,
            60000000)

class ProductAPISecurityTest(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            mobile_number="09120000004",
            email="security@example.com",
            name="Security",
            family="User",
            password="test123"
        )

        self.brand = Brand.objects.create(
            brand_title="Samsung",
            slug="samsung"
        )

        self.product_group = ProductGroup.objects.create(
            group_title="Phones",
            slug="phones"
        )

        self.product = Product.objects.create(
            product_name="Galaxy S24",
            brand=self.brand,
            slug="galaxy-s24",
            image_name="products/test.jpg",
            is_active=True
        )

        self.product.product_group.add(
            self.product_group
        )

        self.store = Store.objects.create(
            user=self.user,
            store_name="Security Store",
            store_phone="09120000005",
            slug="security-store",
            is_active=True
        )

        self.store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=40000000,
            is_active=True
        )

        self.product_url = reverse(
            "api:product-detail",
            kwargs={
                "pk": self.product.pk
            }
        )

        self.store_product_url = reverse(
            "api:store-product-detail",
            kwargs={
                "pk": self.store_product.pk
            }
        )

    def test_product_detail_does_not_allow_put(self):
        response = self.client.put(
            self.product_url,
            {
                "product_name": "Hacked Product"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_product_detail_does_not_allow_post(self):
        response = self.client.post(
            self.product_url,
            {
                "product_name": "Hacked Product"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_product_detail_does_not_allow_patch(self):
        response = self.client.patch(
            self.product_url,
            {
                "product_name": "Hacked Product"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_unauthenticated_can_access_store_product(self):
        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            self.store_product_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_store_product_price_cannot_be_changed_by_get(self):
        old_price = self.store_product.price

        response = self.client.get(
            self.store_product_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.store_product.refresh_from_db()

        self.assertEqual(
            self.store_product.price,
            old_price
        )

    def test_unauthenticated_cannot_update_store_product(self):
        self.client.force_authenticate(
            user=None
        )

        response = self.client.put(
            self.store_product_url,
            {
                "price": 1
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


    def test_store_owner_can_access_own_store_product(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.store_product_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_store_product_does_not_allow_post(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.store_product_url,
            {
                "price": "1"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_store_owner_can_update_own_store_product(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            self.store_product_url,
            {
                "price": "45000000.00"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.store_product.refresh_from_db()

        self.assertEqual(
            str(self.store_product.price),
            "45000000.00"
        )

    def test_store_owner_can_delete_own_store_product(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.delete(
            self.store_product_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            StoreProduct.objects.filter(
                pk=self.store_product.pk
            ).exists()
        )

    def test_store_owner_cannot_change_store(self):
        another_user = CustomUser.objects.create_user(
            mobile_number="09120000010",
            email="other2@example.com",
            name="Other",
            family="User",
            password="test123"
        )

        another_store = Store.objects.create(
            user=another_user,
            store_name="Other Store",
            store_phone="09120000011",
            slug="other-store",
            is_active=True
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            self.store_product_url,
            {
                "store": another_store.id
            }
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_403_FORBIDDEN,
                status.HTTP_405_METHOD_NOT_ALLOWED,
            ]
        )

        self.store_product.refresh_from_db()

        self.assertEqual(
            self.store_product.store,
            self.store
        )

    def test_store_product_product_cannot_be_changed(self):
        another_product = Product.objects.create(
            product_name="Galaxy S25",
            brand=self.brand,
            slug="galaxy-s25",
            image_name="products/test2.jpg",
            is_active=True
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            self.store_product_url,
            {
                "product": another_product.id
            }
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_403_FORBIDDEN,
                status.HTTP_405_METHOD_NOT_ALLOWED,
            ]
        )

        self.store_product.refresh_from_db()

        self.assertEqual(
            self.store_product.product,
            self.product
        )

    def test_other_store_owner_cannot_update_store_product(self):
        another_user = CustomUser.objects.create_user(
            mobile_number="09120000008",
            email="other@example.com",
            name="Other",
            family="User",
            password="test123"
        )

        Store.objects.create(
            user=another_user,
            store_name="Other Store",
            store_phone="09120000009",
            slug="other-store",
            is_active=True
        )

        self.client.force_authenticate(
            user=another_user
        )

        response = self.client.put(
            self.store_product_url,
            {
                "price": 1
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_other_store_owner_cannot_delete_store_product(self):
        another_user = CustomUser.objects.create_user(
            mobile_number="09120000014",
            email="other4@example.com",
            name="Other",
            family="User",
            password="test123"
        )

        Store.objects.create(
            user=another_user,
            store_name="Other Store 4",
            store_phone="09120000015",
            slug="other-store-4",
            is_active=True
        )

        self.client.force_authenticate(
            user=another_user
        )

        response = self.client.delete(
            self.store_product_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertTrue(
            StoreProduct.objects.filter(
                pk=self.store_product.pk
            ).exists()
        )