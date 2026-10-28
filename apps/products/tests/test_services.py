from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import CustomUser, Store
from apps.comment_scoring_favorites.models import Favorite, Scoring
from apps.discounts.models import DiscountBasket, DiscountBasketDetails
from apps.discounts.services import get_price_by_discount
from apps.products.models import (
    Brand,
    Feature,
    FeatureValue,
    Product,
    ProductFeature,
    ProductGroup,
    StoreProduct,
)
from apps.products.services import (
    apply_brand_filter,
    apply_feature_filter,
    apply_product_filter,
    apply_sorting,
    apply_store_filter,
    build_show_count_product,
    get_price_range,
    get_products_by_group,
    get_user_favorite,
    get_user_score,
    paginate_products,
)
from django.http import QueryDict


class ProductServicesTest(TestCase):

    def setUp(self):
        self.price = 1000000

        self.user = CustomUser.objects.create_user(
            mobile_number="09129999999",
            password="123456",
        )

        self.store = Store.objects.create(
            user=self.user,
            store_name="فروشگاه تست",
            store_phone="09121111111",
            is_active=True,
        )

        self.brand = Brand.objects.create(
            brand_title="Samsung",
            slug="samsung",
        )

        self.group = ProductGroup.objects.create(
            group_title="موبایل",
            slug="mobile",
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
            price=self.price,
            is_active=True,
        )

    def test_get_price_without_discount(self):
        price = get_price_by_discount(
            self.store_product
        )

        self.assertEqual(
            price,
            self.price,
        )

    def test_get_price_with_valid_discount(self):
        basket = DiscountBasket.objects.create(
            discount_title="تخفیف",
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            discount=20,
            is_active=True,
        )

        DiscountBasketDetails.objects.create(
            discount_basket=basket,
            store_product=self.store_product,
        )

        price = get_price_by_discount(
            self.store_product
        )

        self.assertEqual(
            price,
            self.price * 0.8,
        )

    def test_get_price_with_multiple_discounts(self):
        basket1 = DiscountBasket.objects.create(
            discount_title="10%",
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            discount=10,
            is_active=True,
        )

        basket2 = DiscountBasket.objects.create(
            discount_title="30%",
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            discount=30,
            is_active=True,
        )

        DiscountBasketDetails.objects.create(
            discount_basket=basket1,
            store_product=self.store_product,
        )

        DiscountBasketDetails.objects.create(
            discount_basket=basket2,
            store_product=self.store_product,
        )

        price = get_price_by_discount(
            self.store_product
        )

        self.assertEqual(
            price,
            self.price * 0.7,
        )

    def test_get_price_with_expired_discount(self):
        basket = DiscountBasket.objects.create(
            discount_title="منقضی",
            start_date=timezone.now() - timedelta(days=10),
            end_date=timezone.now() - timedelta(days=1),
            discount=50,
            is_active=True,
        )

        DiscountBasketDetails.objects.create(
            discount_basket=basket,
            store_product=self.store_product,
        )

        price = get_price_by_discount(
            self.store_product
        )

        self.assertEqual(
            price,
            self.price,
        )

    def test_get_price_with_inactive_discount(self):
        basket = DiscountBasket.objects.create(
            discount_title="غیرفعال",
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            discount=50,
            is_active=False,
        )

        DiscountBasketDetails.objects.create(
            discount_basket=basket,
            store_product=self.store_product,
        )

        price = get_price_by_discount(
            self.store_product
        )

        self.assertEqual(
            price,
            self.price,
        )

    def test_get_user_score_when_score_exists(self):
        Scoring.objects.create(
            store_product=self.store_product,
            scoring_user=self.user,
            score=4,
        )

        score = get_user_score(
            self.store_product,
            self.user,
        )

        self.assertEqual(
            score,
            4,
        )

    def test_get_user_score_when_score_does_not_exist(self):
        score = get_user_score(
            self.store_product,
            self.user,
        )

        self.assertEqual(
            score,
            0,
        )

    def test_get_user_favorite_when_product_is_favorite(self):
        Favorite.objects.create(
            store_product=self.store_product,
            favorite_user=self.user,
        )

        result = get_user_favorite(
            self.store_product,
            self.user,
        )

        self.assertTrue(
            result
        )

    def test_get_user_favorite_when_product_is_not_favorite(self):
        result = get_user_favorite(
            self.store_product,
            self.user,
        )

        self.assertFalse(
            result
        )

    def test_get_products_by_group_returns_group_and_products(self):
        current_group, products = get_products_by_group(
            self.group.slug
        )

        self.assertEqual(
            current_group,
            self.group,
        )

        self.assertIn(
            self.store_product,
            products,
        )

    def test_get_products_by_group_returns_only_active_products(self):
        self.store_product.is_active = False
        self.store_product.save()

        current_group, products = get_products_by_group(
            self.group.slug
        )

        self.assertEqual(
            products.count(),
            0,
        )

    def test_get_products_by_group_returns_only_active_stores(self):
        self.store.is_active = False
        self.store.save()

        current_group, products = get_products_by_group(
            self.group.slug
        )

        self.assertEqual(
            products.count(),
            0,
        )

    def test_get_products_by_group_includes_sub_group_products(self):
        child = ProductGroup.objects.create(
            group_title="گوشی",
            slug="phones",
            group_parent=self.group,
        )

        child_product = Product.objects.create(
            product_name="Galaxy A56",
            brand=self.brand,
            slug="galaxy-a56",
        )

        child_product.product_group.add(
            child
        )

        child_store_product = StoreProduct.objects.create(
            store=self.store,
            product=child_product,
            price=self.price,
            is_active=True,
        )

        current_group, products = get_products_by_group(
            self.group.slug
        )

        self.assertIn(
            self.store_product,
            products,
        )

        self.assertIn(
            child_store_product,
            products,
        )

        # the sub-group page does not show the parent's own products
        child_group, child_products = get_products_by_group(
            child.slug
        )

        self.assertIn(
            child_store_product,
            child_products,
        )

        self.assertNotIn(
            self.store_product,
            child_products,
        )

    def test_get_products_by_group_does_not_duplicate_products(self):
        child = ProductGroup.objects.create(
            group_title="گوشی",
            slug="phones",
            group_parent=self.group,
        )

        # the same product belongs to the main group and to its sub-group
        self.product.product_group.add(
            child
        )

        current_group, products = get_products_by_group(
            self.group.slug
        )

        self.assertEqual(
            products.filter(
                pk=self.store_product.pk
            ).count(),
            1,
        )

    def test_get_products_by_group_invalid_slug(self):
        with self.assertRaises(Exception):
            get_products_by_group(
                "invalid-slug"
            )

    def test_get_price_range(self):
        new_product = Product.objects.create(
            product_name="Galaxy A56",
            brand=self.brand,
            slug="galaxy-a56",
        )

        new_product.product_group.add(
            self.group
        )

        StoreProduct.objects.create(
            store=self.store,
            product=new_product,
            price=500000,
            is_active=True,
        )

        price_range = get_price_range(
            StoreProduct.objects.all()
        )

        self.assertEqual(
            price_range["min"],
            500000,
        )

        self.assertEqual(
            price_range["max"],
            self.price,
        )

    def test_get_price_range_with_empty_queryset(self):
        StoreProduct.objects.all().delete()

        price_range = get_price_range(
            StoreProduct.objects.all()
        )

        self.assertIsNone(
            price_range["min"]
        )

        self.assertIsNone(
            price_range["max"]
        )

    def test_build_show_count_product_less_than_per_page(self):
        result = build_show_count_product(
            product_count=5,
            per_page=10,
        )

        self.assertEqual(
            result,
            [10],
        )

    def test_build_show_count_product_equal_per_page(self):
        result = build_show_count_product(
            product_count=10,
            per_page=10,
        )

        self.assertEqual(
            result,
            [10],
        )

    def test_build_show_count_product_greater_than_per_page(self):
        result = build_show_count_product(
            product_count=35,
            per_page=10,
        )

        self.assertEqual(
            result,
            [10, 20, 40],
        )

    def test_build_show_count_product_large_number(self):
        result = build_show_count_product(
            product_count=100,
            per_page=10,
        )

        self.assertEqual(
            result,
            [10, 20, 40, 80, 160],
        )


class ApplyProductFilterTests(TestCase):

    def setUp(self):
        self.price = 1000000

        self.user = CustomUser.objects.create_user(
            mobile_number="09129999999",
            password="123456",
        )

        self.store = Store.objects.create(
            user=self.user,
            store_name="فروشگاه تست",
            store_phone="09121111111",
            is_active=True,
        )

        self.brand = Brand.objects.create(
            brand_title="Samsung",
            slug="samsung",
        )

        self.group = ProductGroup.objects.create(
            group_title="موبایل",
            slug="mobile",
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
            price=self.price,
            is_active=True,
        )

    def test_apply_product_filter_returns_queryset_and_filter(self):
        get_params = QueryDict("")

        queryset, product_filter = apply_product_filter(
            get_params,
            StoreProduct.objects.all(),
        )

        self.assertEqual(
            queryset.count(),
            1,
        )

        self.assertIsNotNone(
            product_filter
        )

    def test_apply_product_filter_with_empty_queryset(self):
        StoreProduct.objects.all().delete()

        get_params = QueryDict("")

        queryset, product_filter = apply_product_filter(
            get_params,
            StoreProduct.objects.all(),
        )

        self.assertEqual(
            queryset.count(),
            0,
        )

        self.assertIsNotNone(
            product_filter
        )

    def test_apply_product_filter_with_parameters(self):
        get_params = QueryDict(
            "price=500000"
        )

        queryset, product_filter = apply_product_filter(
            get_params,
            StoreProduct.objects.all(),
        )

        self.assertEqual(
            queryset.count(),
            0,
        )

    def test_apply_brand_filter_without_brand(self):
        products = apply_brand_filter(
            [],
            StoreProduct.objects.all(),
        )

        self.assertEqual(
            products.count(),
            1,
        )

    def test_apply_brand_filter_with_brand(self):
        products = apply_brand_filter(
            [self.brand.id],
            StoreProduct.objects.all(),
        )

        self.assertEqual(
            products.count(),
            1,
        )

        self.assertIn(
            self.store_product,
            products,
        )

    def test_apply_brand_filter_with_invalid_brand(self):
        products = apply_brand_filter(
            [999],
            StoreProduct.objects.all(),
        )

        self.assertEqual(
            products.count(),
            0,
        )

    def test_apply_feature_filter_without_feature(self):
        products = apply_feature_filter(
            [],
            StoreProduct.objects.all(),
        )

        self.assertEqual(
            products.count(),
            1,
        )

    def test_apply_feature_filter_with_feature(self):
        feature = Feature.objects.create(
            feature_name="رنگ"
        )

        feature.product_group.add(
            self.group
        )

        feature_value = FeatureValue.objects.create(
            value_title="مشکی",
            feature=feature,
        )

        ProductFeature.objects.create(
            product=self.product,
            feature=feature,
            value="مشکی",
            filter_value=feature_value,
        )

        products = apply_feature_filter(
            [feature_value.id],
            StoreProduct.objects.all(),
        )

        self.assertEqual(
            products.count(),
            1,
        )

        self.assertIn(
            self.store_product,
            products,
        )

    def test_apply_feature_filter_with_invalid_feature(self):
        products = apply_feature_filter(
            [999],
            StoreProduct.objects.all(),
        )

        self.assertEqual(
            products.count(),
            0,
        )

    def test_apply_sorting_default(self):
        products = apply_sorting(
            "0",
            StoreProduct.objects.all(),
        )

        self.assertEqual(
            products.count(),
            1,
        )

    def test_apply_sorting_price_ascending(self):
        product2 = Product.objects.create(
            product_name="Galaxy A56",
            brand=self.brand,
            slug="galaxy-a56",
        )

        product2.product_group.add(
            self.group
        )

        StoreProduct.objects.create(
            store=self.store,
            product=product2,
            price=500000,
            is_active=True,
        )

        products = apply_sorting(
            "1",
            StoreProduct.objects.all(),
        )

        self.assertEqual(
            products.first().price,
            500000,
        )

    def test_apply_sorting_price_descending(self):
        product2 = Product.objects.create(
            product_name="Galaxy A56",
            brand=self.brand,
            slug="galaxy-a56",
        )

        product2.product_group.add(
            self.group
        )

        StoreProduct.objects.create(
            store=self.store,
            product=product2,
            price=500000,
            is_active=True,
        )

        products = apply_sorting(
            "2",
            StoreProduct.objects.all(),
        )

        self.assertEqual(
            products.first().price,
            self.price,
        )

    def test_paginate_products_default_per_page(self):
        page_obj = paginate_products(
            page_number=None,
            per_page=10,
            products=StoreProduct.objects.all(),
        )

        self.assertEqual(
            page_obj.paginator.per_page,
            10,
        )

    def test_paginate_products_orders_unordered_queryset(self):
        page_obj = paginate_products(
            page_number=None,
            per_page=10,
            products=StoreProduct.objects.all(),
        )

        self.assertTrue(
            page_obj.paginator.object_list.ordered
        )

    def test_paginate_products_custom_per_page(self):
        page_obj = paginate_products(
            page_number=None,
            per_page=5,
            products=StoreProduct.objects.all(),
        )

        self.assertEqual(
            page_obj.paginator.per_page,
            5,
        )

    def test_paginate_products_second_page(self):
        for i in range(15):
            product = Product.objects.create(
                product_name=f"Product {i}",
                brand=self.brand,
                slug=f"product-{i}",
            )

            product.product_group.add(
                self.group
            )

            StoreProduct.objects.create(
                store=self.store,
                product=product,
                price=1000 + i,
            )

        page_obj = paginate_products(
            page_number=2,
            per_page=10,
            products=StoreProduct.objects.all(),
        )

        self.assertEqual(
            page_obj.number,
            2,
        )

        self.assertEqual(
            len(page_obj.object_list),
            6,
        )

    def test_apply_store_filter_without_store(self):
        products = apply_store_filter(
            [],
            StoreProduct.objects.all(),
        )

        self.assertEqual(
            products.count(),
            1,
        )

    def test_apply_store_filter_with_store(self):
        products = apply_store_filter(
            [self.store.id],
            StoreProduct.objects.all(),
        )

        self.assertEqual(
            products.count(),
            1,
        )

        self.assertIn(
            self.store_product,
            products,
        )

    def test_apply_store_filter_with_invalid_store(self):
        products = apply_store_filter(
            [999],
            StoreProduct.objects.all(),
        )

        self.assertEqual(
            products.count(),
            0,
        )