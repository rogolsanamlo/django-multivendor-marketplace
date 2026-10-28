from django.core.paginator import Paginator
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from apps.accounts.models import CustomUser, Store
from apps.comment_scoring_favorites.models import Favorite
from apps.products.models import (
    Brand,
    Feature,
    FeatureValue,
    Product,
    ProductFeature,
    ProductGroup,
    StoreProduct,
)


class BaseProductViewTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            mobile_number="09121112233",
            password="1234",
        )

        self.user.is_active = True
        self.user.save()

        self.store = Store.objects.create(
            user=self.user,
            store_name="Digital Store",
            store_phone="09121112222",
            is_active=True,
        )

        self.brand = Brand.objects.create(
            brand_title="Samsung",
            slug="samsung",
        )

        self.group = ProductGroup.objects.create(
            group_title="Mobile",
            slug="mobile",
            is_active=True,
        )

        self.product = Product.objects.create(
            product_name="Galaxy S25",
            brand=self.brand,
            slug="galaxy-s25",
        )

        self.product.product_group.add(
            self.group
        )

        self.store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=15000000,
            is_active=True,
        )

        self.feature = Feature.objects.create(
            feature_name="حافظه"
        )

        self.feature.product_group.add(
            self.group
        )

        self.feature_value = FeatureValue.objects.create(
            value_title="128 گیگابایت",
            feature=self.feature,
        )

        ProductFeature.objects.create(
            product=self.product,
            feature=self.feature,
            value="128GB",
            filter_value=self.feature_value,
        )

    def create_store_product(
        self,
        product_name,
        price,
        brand=None,
        store=None,
        group=None,
        slug=None,
        is_active=True,
    ):
        if brand is None:
            brand = self.brand

        if store is None:
            store = self.store

        if group is None:
            group = self.group

        if slug is None:
            slug = slugify(product_name)

        product = Product.objects.create(
            product_name=product_name,
            brand=brand,
            slug=slug,
            is_active=True,
        )

        product.product_group.add(
            group
        )

        store_product = StoreProduct.objects.create(
            store=store,
            product=product,
            price=price,
            is_active=is_active,
        )

        return product, store_product


class StoreProductDetailViewTests(BaseProductViewTest):

    def test_store_product_detail_view(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "products:product_details",
                kwargs={
                    "pk": self.store_product.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "product_app/product_detail.html",
        )

        self.assertEqual(
            response.context["store_product"],
            self.store_product,
        )

        self.assertEqual(
            response.context["user_score"],
            0,
        )

        self.assertContains(
            response,
            "Galaxy S25",
        )

    def test_store_product_detail_view_guest_user(self):
        response = self.client.get(
            reverse(
                "products:product_details",
                kwargs={
                    "pk": self.store_product.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.context["user_score"],
            0,
        )

    def test_store_product_detail_invalid_pk(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "products:product_details",
                kwargs={
                    "pk": 9999,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )


class CheapestProductsTests(BaseProductViewTest):

    def setUp(self):
        super().setUp()

        self.client.force_login(
            self.user
        )

        self.product2, self.store_product2 = (
            self.create_store_product(
                product_name="Galaxy A56",
                price=12000000,
            )
        )

    def test_get_cheapest_products(self):
        response = self.client.get(
            reverse(
                "products:get_cheapest_products"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "product_app/partials/cheapest_products.html",
        )

        self.assertIn(
            "products",
            response.context,
        )

        self.assertIn(
            "product_groups",
            response.context,
        )

        self.assertGreaterEqual(
            len(response.context["products"]),
            2,
        )

        self.assertIn(
            self.store_product,
            response.context["products"],
        )

        self.assertIn(
            self.store_product2,
            response.context["products"],
        )

    def test_products_are_sorted_by_price(self):
        response = self.client.get(
            reverse(
                "products:get_cheapest_products"
            )
        )

        products = list(
            response.context["products"]
        )

        prices = [
            product.price
            for product in products
        ]

        self.assertEqual(
            prices,
            sorted(prices),
        )

    def test_only_active_products_are_returned(self):
        self.store_product2.is_active = False
        self.store_product2.save()

        response = self.client.get(
            reverse(
                "products:get_cheapest_products"
            )
        )

        self.assertEqual(
            len(response.context["products"]),
            1,
        )

        self.assertEqual(
            response.context["products"][0],
            self.store_product,
        )

    def test_product_has_final_price(self):
        response = self.client.get(
            reverse(
                "products:get_cheapest_products"
            )
        )

        product = response.context["products"][0]

        self.assertTrue(
            hasattr(product, "final_price")
        )

    def test_product_has_is_favorite(self):
        response = self.client.get(
            reverse(
                "products:get_cheapest_products"
            )
        )

        product = response.context["products"][0]

        self.assertTrue(
            hasattr(product, "is_favorite")
        )

        self.assertFalse(
            product.is_favorite
        )

    def test_product_is_favorite_when_user_favorited(self):
        Favorite.objects.create(
            store_product=self.store_product,
            favorite_user=self.user,
        )

        response = self.client.get(
            reverse(
                "products:get_cheapest_products"
            )
        )

        favorite_product = next(
            product
            for product in response.context["products"]
            if product.pk == self.store_product.pk
        )

        self.assertTrue(
            favorite_product.is_favorite
        )

    def test_cheapest_products_guest_user(self):
        self.client.logout()

        response = self.client.get(
            reverse(
                "products:get_cheapest_products"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        product = response.context["products"][0]

        self.assertTrue(
            hasattr(product, "is_favorite")
        )

        self.assertFalse(
            product.is_favorite
        )


class LastProductsTests(BaseProductViewTest):

    def setUp(self):
        super().setUp()

        self.client.force_login(
            self.user
        )

        self.product2, self.store_product2 = (
            self.create_store_product(
                product_name="Galaxy A56",
                price=12000000,
            )
        )

    def test_get_last_products(self):
        response = self.client.get(
            reverse(
                "products:get_last_products"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "product_app/partials/last_products.html",
        )

        self.assertIn(
            "products",
            response.context,
        )

        self.assertIn(
            "product_groups",
            response.context,
        )

        self.assertGreaterEqual(
            len(response.context["products"]),
            2,
        )

        self.assertIn(
            self.store_product,
            response.context["products"],
        )

        self.assertIn(
            self.store_product2,
            response.context["products"],
        )

    def test_products_are_sorted_by_register_date(self):
        response = self.client.get(
            reverse(
                "products:get_last_products"
            )
        )

        products = list(
            response.context["products"]
        )

        dates = [
            product.register_date
            for product in products
        ]

        self.assertEqual(
            dates,
            sorted(
                dates,
                reverse=True,
            ),
        )

    def test_only_active_products_are_returned(self):
        self.store_product2.is_active = False
        self.store_product2.save()

        response = self.client.get(
            reverse(
                "products:get_last_products"
            )
        )

        self.assertEqual(
            len(response.context["products"]),
            1,
        )

        self.assertEqual(
            response.context["products"][0],
            self.store_product,
        )

    def test_products_have_final_price(self):
        response = self.client.get(
            reverse(
                "products:get_last_products"
            )
        )

        product = response.context["products"][0]

        self.assertTrue(
            hasattr(product, "final_price")
        )

    def test_products_have_is_favorite(self):
        response = self.client.get(
            reverse(
                "products:get_last_products"
            )
        )

        product = response.context["products"][0]

        self.assertTrue(
            hasattr(product, "is_favorite")
        )

        self.assertFalse(
            product.is_favorite
        )


class RelatedProductsTests(BaseProductViewTest):

    def setUp(self):
        super().setUp()

        self.client.force_login(
            self.user
        )

        self.product2, self.store_product2 = (
            self.create_store_product(
                product_name="Galaxy A56",
                price=12000000,
            )
        )

        self.group2 = ProductGroup.objects.create(
            group_title="Laptop",
            slug="laptop",
            is_active=True,
        )

        self.product3, self.store_product3 = (
            self.create_store_product(
                product_name="MacBook",
                price=50000000,
                group=self.group2,
                slug="macbook",
            )
        )

    def test_get_related_products(self):
        response = self.client.get(
            reverse(
                "products:get_related_products",
                kwargs={
                    "slug": self.product.slug
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "product_app/partials/related_products.html",
        )

        self.assertIn(
            "related_products",
            response.context,
        )

    def test_related_product_exists(self):
        response = self.client.get(
            reverse(
                "products:get_related_products",
                kwargs={
                    "slug": self.product.slug
                },
            )
        )

        self.assertIn(
            self.store_product2,
            response.context["related_products"],
        )

    def test_current_product_is_not_returned(self):
        response = self.client.get(
            reverse(
                "products:get_related_products",
                kwargs={
                    "slug": self.product.slug
                },
            )
        )

        self.assertNotIn(
            self.store_product,
            response.context["related_products"],
        )

    def test_product_from_another_group_is_not_returned(self):
        response = self.client.get(
            reverse(
                "products:get_related_products",
                kwargs={
                    "slug": self.product.slug
                },
            )
        )

        self.assertNotIn(
            self.store_product3,
            response.context["related_products"],
        )

    def test_invalid_slug_returns_404(self):
        response = self.client.get(
            reverse(
                "products:get_related_products",
                kwargs={
                    "slug": "invalid-slug"
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_inactive_product_is_not_returned(self):
        self.product2.is_active = False
        self.product2.save()

        response = self.client.get(
            reverse(
                "products:get_related_products",
                kwargs={
                    "slug": self.product.slug
                },
            )
        )

        self.assertNotIn(
            self.store_product2,
            response.context["related_products"],
        )

    def test_inactive_store_product_is_not_returned(self):
        self.store_product2.is_active = False
        self.store_product2.save()

        response = self.client.get(
            reverse(
                "products:get_related_products",
                kwargs={
                    "slug": self.product.slug
                },
            )
        )

        self.assertNotIn(
            self.store_product2,
            response.context["related_products"],
        )

    def test_inactive_store_is_not_returned(self):
        self.store.is_active = False
        self.store.save()

        response = self.client.get(
            reverse(
                "products:get_related_products",
                kwargs={
                    "slug": self.product.slug
                },
            )
        )

        self.assertEqual(
            len(response.context["related_products"]),
            0,
        )


class ProductGroupsViewTests(BaseProductViewTest):

    def setUp(self):
        super().setUp()

        self.client.force_login(
            self.user
        )

    def test_product_groups_view(self):
        response = self.client.get(
            reverse(
                "products:product_groups"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "product_app/product_groups.html",
        )

        self.assertIn(
            "product_groups",
            response.context,
        )

    def test_only_active_groups_are_returned(self):
        self.group.is_active = False
        self.group.save()

        response = self.client.get(
            reverse(
                "products:product_groups"
            )
        )

        self.assertEqual(
            len(response.context["product_groups"]),
            0,
        )

    def test_group_exists_in_context(self):
        response = self.client.get(
            reverse(
                "products:product_groups"
            )
        )

        self.assertIn(
            self.group,
            response.context["product_groups"],
        )


class FeaturesForFilterTests(BaseProductViewTest):

    def setUp(self):
        super().setUp()

        self.client.force_login(
            self.user
        )

        self.feature = Feature.objects.create(
            feature_name="Color"
        )

        self.feature.product_group.add(
            self.group
        )

        self.value1 = FeatureValue.objects.create(
            value_title="Black",
            feature=self.feature,
        )

        self.value2 = FeatureValue.objects.create(
            value_title="White",
            feature=self.feature,
        )

    def test_get_features_for_filter(self):
        response = self.client.get(
            reverse(
                "products:get_features_for_filter",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "product_app/partials/feature_filter.html",
        )

        self.assertIn(
            "feature_dict",
            response.context,
        )

    def test_feature_exists_in_context(self):
        response = self.client.get(
            reverse(
                "products:get_features_for_filter",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        self.assertIn(
            self.feature,
            response.context["feature_dict"],
        )

    def test_feature_values_exist(self):
        response = self.client.get(
            reverse(
                "products:get_features_for_filter",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        feature_dict = response.context["feature_dict"]

        self.assertIn(
            self.value1,
            feature_dict[self.feature],
        )

        self.assertIn(
            self.value2,
            feature_dict[self.feature],
        )

    def test_invalid_group_slug_returns_404(self):
        response = self.client.get(
            reverse(
                "products:get_features_for_filter",
                kwargs={
                    "slug": "invalid-group"
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )


class BrandsViewTests(BaseProductViewTest):

    def setUp(self):
        super().setUp()

        self.client.force_login(
            self.user
        )

        self.brand2 = Brand.objects.create(
            brand_title="Apple",
            slug="apple",
        )

        self.product2, self.store_product2 = (
            self.create_store_product(
                product_name="iPhone 16",
                price=50000000,
                brand=self.brand2,
                slug="iphone-16",
            )
        )

    def test_get_brands(self):
        response = self.client.get(
            reverse(
                "products:get_brands",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "product_app/partials/brands.html",
        )

        self.assertIn(
            "brands",
            response.context,
        )

    def test_brands_exist_in_context(self):
        response = self.client.get(
            reverse(
                "products:get_brands",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        brands = response.context["brands"]

        self.assertIn(
            self.brand,
            brands,
        )

        self.assertIn(
            self.brand2,
            brands,
        )

    def test_inactive_store_product_brand_not_returned(self):
        self.store_product2.is_active = False
        self.store_product2.save()

        response = self.client.get(
            reverse(
                "products:get_brands",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        self.assertNotIn(
            self.brand2,
            response.context["brands"],
        )

    def test_invalid_group_slug_returns_404(self):
        response = self.client.get(
            reverse(
                "products:get_brands",
                kwargs={
                    "slug": "invalid-group"
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_brand_has_count_annotation(self):
        response = self.client.get(
            reverse(
                "products:get_brands",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        brand = response.context["brands"].first()

        self.assertTrue(
            hasattr(brand, "count")
        )

        self.assertIsInstance(
            brand.count,
            int,
        )


class StoresViewTests(BaseProductViewTest):

    def setUp(self):
        super().setUp()

        self.client.force_login(
            self.user
        )

        self.user2 = CustomUser.objects.create_user(
            mobile_number="09123334455",
            password="1234",
        )

        self.store2 = Store.objects.create(
            user=self.user2,
            store_name="Mobile Center",
            store_phone="09123334466",
            is_active=True,
        )

        self.product2, self.store_product2 = (
            self.create_store_product(
                product_name="Galaxy A56",
                price=12000000,
                store=self.store2,
                slug="galaxy-a56",
            )
        )

    def test_get_stores(self):
        response = self.client.get(
            reverse(
                "products:get_stores",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "product_app/partials/stores.html",
        )

        self.assertIn(
            "stores",
            response.context,
        )

    def test_stores_exist_in_context(self):
        response = self.client.get(
            reverse(
                "products:get_stores",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        stores = response.context["stores"]

        self.assertIn(
            self.store,
            stores,
        )

        self.assertIn(
            self.store2,
            stores,
        )

    def test_inactive_store_not_returned(self):
        self.store2.is_active = False
        self.store2.save()

        response = self.client.get(
            reverse(
                "products:get_stores",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        self.assertNotIn(
            self.store2,
            response.context["stores"],
        )

    def test_inactive_store_product_not_returned(self):
        self.store_product2.is_active = False
        self.store_product2.save()

        response = self.client.get(
            reverse(
                "products:get_stores",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        self.assertNotIn(
            self.store2,
            response.context["stores"],
        )

    def test_invalid_group_slug_returns_404(self):
        response = self.client.get(
            reverse(
                "products:get_stores",
                kwargs={
                    "slug": "invalid-group"
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_store_has_count_annotation(self):
        response = self.client.get(
            reverse(
                "products:get_stores",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        store = response.context["stores"].first()

        self.assertTrue(
            hasattr(store, "count")
        )

        self.assertIsInstance(
            store.count,
            int,
        )


class ProductsByGroupViewTests(BaseProductViewTest):

    def setUp(self):
        super().setUp()

        self.client.force_login(
            self.user
        )

        self.product2, self.store_product2 = (
            self.create_store_product(
                product_name="Galaxy A56",
                price=12000000,
                slug="galaxy-a56",
            )
        )

    def test_products_by_group(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "product_app/products.html",
        )

    def test_context_exists(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        for key in [
            "products",
            "current_group",
            "page_obj",
            "product_count",
            "show_count_product",
            "sort_type",
            "filter",
            "res_aggre",
        ]:
            self.assertIn(
                key,
                response.context,
            )

    def test_current_group(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        self.assertEqual(
            response.context["current_group"],
            self.group,
        )

    def test_product_count(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        self.assertEqual(
            response.context["product_count"],
            2,
        )

    def test_invalid_slug_returns_404(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": "wrong-group"
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_only_active_products(self):
        self.store_product2.is_active = False
        self.store_product2.save()

        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        self.assertEqual(
            response.context["product_count"],
            1,
        )


class ProductsByGroupFilterTests(BaseProductViewTest):

    def setUp(self):
        super().setUp()

        self.client.force_login(
            self.user
        )

        self.brand2 = Brand.objects.create(
            brand_title="Apple",
            slug="apple",
        )

        self.product2, self.store_product2 = (
            self.create_store_product(
                product_name="iPhone 16",
                price=50000000,
                brand=self.brand2,
                slug="iphone-16",
            )
        )

        self.feature = Feature.objects.create(
            feature_name="Color"
        )

        self.feature.product_group.add(
            self.group
        )

        self.feature_value = FeatureValue.objects.create(
            value_title="Black",
            feature=self.feature,
        )

        ProductFeature.objects.create(
            product=self.product2,
            feature=self.feature,
            value="Black",
            filter_value=self.feature_value,
        )

        self.user2 = CustomUser.objects.create_user(
            mobile_number="09120000001",
            password="1234",
        )

        self.store2 = Store.objects.create(
            user=self.user2,
            store_name="Apple Store",
            store_phone="09120000002",
            is_active=True,
        )

        self.store_product3 = StoreProduct.objects.create(
            store=self.store2,
            product=self.product2,
            price=51000000,
            is_active=True,
        )

    def test_brand_filter(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            ),
            {
                "brand": self.brand2.id
            },
        )

        for item in response.context["products"]:
            self.assertEqual(
                item.product.brand,
                self.brand2,
            )

        self.assertEqual(
            len(response.context["products"]),
            2,
        )

    def test_store_filter(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            ),
            {
                "store": self.store2.id
            },
        )

        for item in response.context["products"]:
            self.assertEqual(
                item.store,
                self.store2,
            )

        self.assertEqual(
            len(response.context["products"]),
            1,
        )

    def test_feature_filter(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            ),
            {
                "feature": self.feature_value.id
            },
        )

        self.assertEqual(
            len(response.context["products"]),
            2,
        )

    def test_without_filter(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        self.assertEqual(
            response.context["product_count"],
            3,
        )


class ProductsByGroupSortingTests(BaseProductViewTest):

    def setUp(self):
        super().setUp()

        self.client.force_login(
            self.user
        )

        self.store_product.price = 30000000
        self.store_product.save()

        self.product2, self.store_product2 = (
            self.create_store_product(
                product_name="Galaxy A56",
                price=10000000,
                slug="galaxy-a56",
            )
        )

        self.product3, self.store_product3 = (
            self.create_store_product(
                product_name="Galaxy A36",
                price=20000000,
                slug="galaxy-a36",
            )
        )

    def test_default_sort_type(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        self.assertEqual(
            response.context["sort_type"],
            "0",
        )

    def test_sort_price_ascending(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            ),
            {
                "sort_type": "1"
            },
        )

        products = list(
            response.context["products"]
        )

        prices = [
            product.price
            for product in products
        ]

        self.assertEqual(
            prices,
            sorted(prices),
        )

    def test_sort_price_descending(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            ),
            {
                "sort_type": "2"
            },
        )

        products = list(
            response.context["products"]
        )

        prices = [
            product.price
            for product in products
        ]

        self.assertEqual(
            prices,
            sorted(
                prices,
                reverse=True,
            ),
        )

    def test_invalid_sort_type(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            ),
            {
                "sort_type": "100"
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.context["sort_type"],
            "100",
        )


class ProductsByGroupPaginationTests(BaseProductViewTest):

    def setUp(self):
        super().setUp()

        self.client.force_login(
            self.user
        )

        for i in range(1, 16):
            self.create_store_product(
                product_name=f"Product {i}",
                price=i * 100000,
                slug=f"product-{i}",
            )

    def test_default_per_page(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        self.assertEqual(
            len(response.context["page_obj"]),
            10,
        )

    def test_custom_per_page(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            ),
            {
                "per_page": 5
            },
        )

        self.assertEqual(
            len(response.context["page_obj"]),
            5,
        )

    def test_second_page(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            ),
            {
                "page": 2
            },
        )

        self.assertEqual(
            response.context["page_obj"].number,
            2,
        )

    def test_page_has_paginator(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        self.assertIsInstance(
            response.context["page_obj"].paginator,
            Paginator,
        )

    def test_show_count_product_exists(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        self.assertIn(
            "show_count_product",
            response.context,
        )

        self.assertIsInstance(
            response.context["show_count_product"],
            list,
        )

    def test_show_count_product_keeps_default_option_after_choice(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            ),
            {
                "per_page": 20
            },
        )

        self.assertIn(
            10,
            response.context["show_count_product"],
        )

        self.assertIn(
            20,
            response.context["show_count_product"],
        )

        self.assertEqual(
            response.context["per_page"],
            20,
        )

    def test_show_count_product_always_offers_fixed_choices(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        for choice in (5, 10, 20, 40):
            self.assertIn(
                choice,
                response.context["show_count_product"],
            )

    def test_base_query_keeps_sort_and_per_page_but_not_page(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            ),
            {
                "sort_type": "1",
                "per_page": 5,
                "page": 2,
            },
        )

        base_query = response.context["base_query"]

        self.assertIn(
            "sort_type=1",
            base_query,
        )

        self.assertIn(
            "per_page=5",
            base_query,
        )

        self.assertNotIn(
            "page=2",
            base_query,
        )

    def test_product_count(self):
        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={
                    "slug": self.group.slug
                },
            )
        )

        self.assertEqual(
            response.context["product_count"],
            16,
        )


class PopularProductGroupsTests(BaseProductViewTest):

    def setUp(self):
        super().setUp()

        self.client.force_login(
            self.user
        )

    def test_popular_product_groups(self):
        response = self.client.get(
            reverse(
                "products:get_popular_product_groups"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "product_app/partials/popular_product_groups.html",
        )

        self.assertIn(
            "product_groups",
            response.context,
        )

    def test_group_exists(self):
        response = self.client.get(
            reverse(
                "products:get_popular_product_groups"
            )
        )

        self.assertIn(
            self.group,
            response.context["product_groups"],
        )

    def test_only_active_groups(self):
        self.group.is_active = False
        self.group.save()

        response = self.client.get(
            reverse(
                "products:get_popular_product_groups"
            )
        )

        self.assertEqual(
            len(response.context["product_groups"]),
            0,
        )


class ProductGroupsMenuTests(BaseProductViewTest):

    def setUp(self):
        super().setUp()

        self.client.force_login(
            self.user
        )

        self.child_group = ProductGroup.objects.create(
            group_title="Android",
            slug="android",
            is_active=True,
            group_parent=self.group,
        )

    def test_get_product_groups_menu(self):
        response = self.client.get(
            reverse(
                "products:get_product_groups_menu"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "product_app/partials/product_groups_menu.html",
        )

        self.assertIn(
            "product_groups",
            response.context,
        )

    def test_only_root_groups_are_returned(self):
        response = self.client.get(
            reverse(
                "products:get_product_groups_menu"
            )
        )

        groups = response.context["product_groups"]

        self.assertIn(
            self.group,
            groups,
        )

        self.assertNotIn(
            self.child_group,
            groups,
        )

    def test_inactive_group_not_returned(self):
        self.group.is_active = False
        self.group.save()

        response = self.client.get(
            reverse(
                "products:get_product_groups_menu"
            )
        )

        self.assertEqual(
            len(response.context["product_groups"]),
            0,
        )


class CompareStoreProductViewTests(BaseProductViewTest):

    def setUp(self):
        super().setUp()

        self.client.force_login(
            self.user
        )

    def test_compare_store_product_view(self):
        response = self.client.get(
            reverse(
                "products:compare_store_list"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "product_app/compare_store_list.html",
        )

        self.assertIn(
            "compare_store_product",
            response.context,
        )


class AddStoreProductCompareTests(BaseProductViewTest):

    def setUp(self):
        super().setUp()

        self.client.force_login(
            self.user
        )

    def test_add_first_store_product(self):
        response = self.client.get(
            reverse(
                "products:add_store_product_to_compare"
            ),
            {
                "storeProductId": self.store_product.id
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "به لیست مقایسه اضافه شد",
        )

        session = self.client.session

        self.assertEqual(
            session["compare_store_product"],
            [self.store_product.id],
        )

    def test_add_duplicate_store_product(self):
        session = self.client.session

        session["compare_store_product"] = [
            self.store_product.id
        ]

        session.save()

        response = self.client.get(
            reverse(
                "products:add_store_product_to_compare"
            ),
            {
                "storeProductId": self.store_product.id
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "به لیست مقایسه اضافه شد",
        )

        session = self.client.session

        self.assertEqual(
            len(
                session["compare_store_product"]
            ),
            1,
        )

        self.assertEqual(
            session["compare_store_product"][0],
            self.store_product.id,
        )


class DeleteStoreProductCompareTests(BaseProductViewTest):

    def setUp(self):
        super().setUp()

        self.client.force_login(
            self.user
        )

        session = self.client.session

        session["compare_store_product"] = [
            self.store_product.id
        ]

        session.save()

    def test_delete_store_product(self):
        response = self.client.get(
            reverse(
                "products:delete_store_product_from_compare"
            ),
            {
                "storeProductId": self.store_product.id
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertRedirects(
            response,
            reverse(
                "products:compare_store_table"
            ),
        )

        session = self.client.session

        self.assertEqual(
            session["compare_store_product"],
            [],
        )

    def test_delete_store_product_not_in_session(self):
        response = self.client.get(
            reverse(
                "products:delete_store_product_from_compare"
            ),
            {
                "storeProductId": 9999
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertRedirects(
            response,
            reverse(
                "products:compare_store_table"
            ),
        )

        session = self.client.session

        self.assertNotIn(
            9999,
            session.get(
                "compare_store_product",
                [],
            ),
        )


class CompareStoreTableTests(BaseProductViewTest):

    def test_compare_store_table(self):
        session = self.client.session

        session["compare_store_product"] = [
            self.store_product.id
        ]

        session.save()

        response = self.client.get(
            reverse(
                "products:compare_store_table"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "product_app/partials/compare_store_table.html",
        )

        self.assertIn(
            "store_products",
            response.context,
        )

        self.assertIn(
            "features",
            response.context,
        )

        self.assertIn(
            self.store_product,
            response.context["store_products"],
        )

        self.assertIn(
            self.feature,
            response.context["features"],
        )

    def test_compare_store_table_empty(self):
        response = self.client.get(
            reverse(
                "products:compare_store_table"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.context["store_products"]),
            0,
        )

        self.assertEqual(
            len(response.context["features"]),
            0,
        )


class NavMegamenuViewTests(BaseProductViewTest):

    def test_nav_megamenu_lists_root_groups(self):
        response = self.client.get(
            reverse("products:get_nav_megamenu")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "product_app/partials/nav_megamenu.html"
        )

        self.assertContains(
            response,
            self.group.group_title
        )
