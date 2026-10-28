from django.urls import reverse

from apps.products.models import (
    Brand,
    Product,
    ProductGroup,
    StoreProduct,
)
from apps.tests.base import BaseAccountTest


class SearchResultsViewTest(BaseAccountTest):

    def setUp(self):
        super().setUp()

        self.brand = Brand.objects.create(
            brand_title="Test Brand",
            slug="test-brand",
            image_name=self.create_test_image(),
        )

        self.product_group = ProductGroup.objects.create(
            group_title="Test Group",
            slug="test-group",
            image_name=self.create_test_image(),
        )

        self.product = Product.objects.create(
            product_name="Test Laptop",
            brand=self.brand,
            slug="test-laptop",
            image_name=self.create_test_image(),
            description="Powerful laptop for programming",
        )

        self.product.product_group.add(
            self.product_group
        )

        self.store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=100000,
        )

    def test_search_view_returns_active_product(self):
        response = self.client.get(
            reverse("search:search_view"),
            {"q": "Laptop"},
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Test Laptop",
        )

    def test_search_by_product_description(self):
        response = self.client.get(
            reverse("search:search_view"),
            {"q": "programming"},
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Test Laptop",
        )

    def test_search_is_case_insensitive(self):
        response = self.client.get(
            reverse("search:search_view"),
            {"q": "lApToP"},
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Test Laptop",
        )

    def test_inactive_store_product_is_not_returned(self):
        self.store_product.is_active = False
        self.store_product.save()

        response = self.client.get(
            reverse("search:search_view"),
            {"q": "Laptop"},
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertNotContains(
            response,
            "Test Laptop",
        )

    def test_empty_query_returns_active_products(self):
        response = self.client.get(
            reverse("search:search_view")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Test Laptop",
        )

    def test_search_with_no_matching_product_returns_empty_result(self):
        response = self.client.get(
            reverse("search:search_view"),
            {"q": "Mobile Phone"},
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertNotContains(
            response,
            "Test Laptop",
        )

    def test_search_returns_only_matching_products(self):
        second_product = Product.objects.create(
            product_name="Test Mobile",
            brand=self.brand,
            slug="test-mobile",
            image_name=self.create_test_image(),
            description="A mobile phone",
        )

        second_product.product_group.add(
            self.product_group
        )

        StoreProduct.objects.create(
            store=self.store,
            product=second_product,
            price=200000,
        )

        response = self.client.get(
            reverse("search:search_view"),
            {"q": "Laptop"},
        )

        self.assertContains(
            response,
            "Test Laptop",
        )

        self.assertNotContains(
            response,
            "Test Mobile",
        )

    def test_search_with_whitespace_query(self):
        response = self.client.get(
            reverse("search:search_view"),
            {"q": "   Laptop   "},
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Test Laptop",
        )

    def test_search_without_query_does_not_fail(self):
        response = self.client.get(
            reverse("search:search_view")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_search_product_name_partial_match(self):
        response = self.client.get(
            reverse("search:search_view"),
            {"q": "Lap"},
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Test Laptop",
        )

    def test_search_context_contains_products(self):
        response = self.client.get(
            reverse("search:search_view"),
            {"q": "Laptop"},
        )

        self.assertIn(
            "products",
            response.context,
        )

        self.assertIn(
            self.store_product,
            response.context["products"],
        )