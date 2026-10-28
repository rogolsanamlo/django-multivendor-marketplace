from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import CustomUser, Store
from apps.products.models import (
    Brand,
    Feature,
    FeatureValue,
    Product,
    ProductGroup,
    StoreProduct,
)


class BrandModelTest(TestCase):

    def test_create_brand(self):
        brand = Brand.objects.create(
            brand_title="Samsung",
            slug="samsung"
        )

        self.assertEqual(
            brand.brand_title,
            "Samsung"
        )
        self.assertEqual(
            str(brand),
            "Samsung"
        )


class ProductGroupModelTest(TestCase):

    def test_create_product_group(self):
        group = ProductGroup.objects.create(
            group_title="Mobile",
            slug="mobile"
        )

        self.assertEqual(
            group.group_title,
            "Mobile"
        )
        self.assertTrue(group.is_active)
        self.assertEqual(
            str(group),
            "Mobile"
        )

    def test_product_group_parent_relation(self):
        parent = ProductGroup.objects.create(
            group_title="Digital",
            slug="digital"
        )

        child = ProductGroup.objects.create(
            group_title="Mobile",
            slug="mobile",
            group_parent=parent
        )

        self.assertEqual(
            child.group_parent,
            parent
        )
        self.assertIn(
            child,
            parent.groups.all()
        )


class FeatureModelTest(TestCase):

    def test_create_feature(self):
        group = ProductGroup.objects.create(
            group_title="Laptop",
            slug="laptop"
        )

        feature = Feature.objects.create(
            feature_name="RAM"
        )

        feature.product_group.add(group)

        self.assertEqual(
            feature.feature_name,
            "RAM"
        )
        self.assertIn(
            group,
            feature.product_group.all()
        )
        self.assertEqual(
            str(feature),
            "RAM"
        )


class FeatureValueModelTest(TestCase):

    def test_create_feature_value(self):
        feature = Feature.objects.create(
            feature_name="Color"
        )

        value = FeatureValue.objects.create(
            value_title="Black",
            feature=feature
        )

        self.assertEqual(
            value.value_title,
            "Black"
        )
        self.assertEqual(
            value.feature,
            feature
        )
        self.assertEqual(
            str(value),
            f"{value.id}-Black"
        )


class ProductModelTest(TestCase):

    def setUp(self):
        self.brand = Brand.objects.create(
            brand_title="Apple",
            slug="apple"
        )

        self.group = ProductGroup.objects.create(
            group_title="Phone",
            slug="phone"
        )

        self.product = Product.objects.create(
            product_name="iPhone 15",
            brand=self.brand,
            slug="iphone-15"
        )

        self.product.product_group.add(self.group)

    def test_create_product(self):
        self.assertEqual(
            self.product.product_name,
            "iPhone 15"
        )
        self.assertEqual(
            str(self.product),
            "iPhone 15"
        )

    def test_product_brand_relation(self):
        self.assertEqual(
            self.product.brand,
            self.brand
        )
        self.assertIn(
            self.product,
            self.brand.products_of_brands.all()
        )

    def test_product_group_relation(self):
        self.assertIn(
            self.group,
            self.product.product_group.all()
        )


class StoreModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            mobile_number="09121112233",
            password="test123456"
        )

        self.store = Store.objects.create(
            user=self.user,
            store_name="فروشگاه مرکزی",
            store_phone="09123334444"
        )

    def test_store_str_method(self):
        self.assertEqual(
            str(self.store),
            "فروشگاه مرکزی"
        )

    def test_user_can_not_have_two_stores(self):
        with self.assertRaises(IntegrityError):
            Store.objects.create(
                user=self.user,
                store_name="فروشگاه دوم",
                store_phone="09125556666"
            )


class StoreProductModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            mobile_number="09121112233",
            password="test123456"
        )

        self.store = Store.objects.create(
            user=self.user,
            store_name="فروشگاه مرکزی",
            store_phone="09123334444"
        )

        self.brand = Brand.objects.create(
            brand_title="Samsung",
            slug="samsung"
        )

        self.product = Product.objects.create(
            product_name="Galaxy S25",
            slug="galaxy-s25",
            brand=self.brand
        )

    def test_create_store_product(self):
        store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product
        )

        self.assertEqual(
            store_product.store,
            self.store
        )
        self.assertEqual(
            store_product.product,
            self.product
        )

    def test_get_absolute_url_uses_store_product_pk(self):
        store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product
        )

        self.assertEqual(
            store_product.get_absolute_url(),
            reverse(
                "products:product_details",
                kwargs={
                    "pk": store_product.pk,
                }
            )
        )

    def test_store_products_relation(self):
        store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product
        )

        self.assertIn(
            store_product,
            self.store.products.all()
        )

    def test_product_store_products_relation(self):
        store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product
        )

        self.assertIn(
            store_product,
            self.product.store_products.all()
        )