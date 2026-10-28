import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import CustomUser, Store
from apps.products.models import (
    Brand,
    Product,
    ProductGroup,
    StoreProduct,
)


class SearchAPITests(APITestCase):

    def setUp(self):

        self.user = CustomUser.objects.create_user(
            mobile_number="09120000001",
            password="test123",
            email="09120000001@example.com",
            name="Test",
            family="User",
        )

        self.store = Store.objects.create(
            user=self.user,
            store_name="Test Store",
            store_phone="09120000002",
            address="Test Address",
            is_active=True,
        )

        self.brand = Brand.objects.create(
            brand_title="Test Brand",
            slug=f"test-brand-{uuid.uuid4().hex[:10]}",
        )

        self.product_group = ProductGroup.objects.create(
            group_title="Test Group",
            slug=f"test-group-{uuid.uuid4().hex[:10]}",
        )

        self.product = Product.objects.create(
            product_name="Test Yogurt",
            brand=self.brand,
            slug=f"test-yogurt-{uuid.uuid4().hex[:10]}",
            is_active=True,
        )

        self.product.product_group.add(
            self.product_group
        )

        self.store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=50000,
            is_active=True,
        )

        self.inactive_product = Product.objects.create(
            product_name="Inactive Yogurt",
            brand=self.brand,
            slug=f"inactive-yogurt-{uuid.uuid4().hex[:10]}",
            is_active=True,
        )

        self.inactive_store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.inactive_product,
            price=60000,
            is_active=False,
        )

    def test_search_api_is_accessible_without_authentication(self):

        url = reverse("api:search")

        response = self.client.get(
            url,
            {"q": "Yogurt"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_search_by_product_name(self):

        url = reverse("api:search")

        response = self.client.get(
            url,
            {"q": "Test Yogurt"},
        )

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
            self.store_product.id,
        )

    def test_search_by_description(self):

        self.product.description = "Fresh milk yogurt"
        self.product.save()

        url = reverse("api:search")

        response = self.client.get(
            url,
            {"q": "Fresh milk"},
        )

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
            self.store_product.id,
        )

    def test_inactive_store_product_is_not_returned(self):

        url = reverse("api:search")

        response = self.client.get(
            url,
            {"q": "Inactive Yogurt"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            0,
        )

    def test_search_without_query_returns_active_products(self):

        url = reverse("api:search")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = [
            item["id"]
            for item in response.data
        ]
        self.assertIn(
            self.store_product.id,
            returned_ids,
        )

        self.assertNotIn(
            self.inactive_store_product.id,
            returned_ids,
        )

    def test_search_with_no_matching_product_returns_empty_list(self):

        url = reverse("api:search")

        response = self.client.get(
            url,
            {"q": "SomethingThatDoesNotExist"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            0,
        )

    def test_search_query_is_stripped(self):

        url = reverse("api:search")

        response = self.client.get(
            url,
            {"q": "   Test Yogurt   "},
        )

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
            self.store_product.id,
        )
