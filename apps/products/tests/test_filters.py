from django.test import TestCase

from apps.accounts.models import CustomUser, Store
from apps.products.filters import ProductFilter
from apps.products.models import (
    Brand,
    Product,
    ProductGroup,
    StoreProduct,
)


class ProductFilterTests(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            mobile_number="09120001122",
            password="testpass"
        )

        self.store = Store.objects.create(
            user=self.user,
            store_name="فروشگاه تست",
            store_phone="09121112233",
            is_active=True
        )

        self.brand = Brand.objects.create(
            brand_title="TestBrand",
            slug="test-brand"
        )

        self.group = ProductGroup.objects.create(
            group_title="TestGroup",
            slug="test-group"
        )

        self.product1 = Product.objects.create(
            product_name="Product 1",
            brand=self.brand,
            slug="product-1"
        )

        self.product1.product_group.add(
            self.group
        )

        self.sp1 = StoreProduct.objects.create(
            store=self.store,
            product=self.product1,
            price=500000,
            is_active=True
        )

        self.product2 = Product.objects.create(
            product_name="Product 2",
            brand=self.brand,
            slug="product-2"
        )

        self.product2.product_group.add(
            self.group
        )

        self.sp2 = StoreProduct.objects.create(
            store=self.store,
            product=self.product2,
            price=1000000,
            is_active=True
        )

        self.product3 = Product.objects.create(
            product_name="Product 3",
            brand=self.brand,
            slug="product-3"
        )

        self.product3.product_group.add(
            self.group
        )

        self.sp3 = StoreProduct.objects.create(
            store=self.store,
            product=self.product3,
            price=1500000,
            is_active=True
        )

    def test_no_filter_returns_all(self):
        product_filter = ProductFilter(
            data={},
            queryset=StoreProduct.objects.all()
        )

        self.assertEqual(
            product_filter.qs.count(),
            3
        )

    def test_filter_price_lte_returns_correct_products(self):
        product_filter = ProductFilter(
            data={"price": 1000000},
            queryset=StoreProduct.objects.all()
        )

        queryset = product_filter.qs

        self.assertEqual(
            queryset.count(),
            2
        )
        self.assertIn(
            self.sp1,
            queryset
        )
        self.assertIn(
            self.sp2,
            queryset
        )
        self.assertNotIn(
            self.sp3,
            queryset
        )

    def test_filter_price_no_match(self):
        product_filter = ProductFilter(
            data={"price": 100000},
            queryset=StoreProduct.objects.all()
        )

        self.assertEqual(
            product_filter.qs.count(),
            0
        )

    def test_filter_price_exact_boundary(self):
        product_filter = ProductFilter(
            data={"price": 1500000},
            queryset=StoreProduct.objects.all()
        )

        queryset = product_filter.qs

        self.assertEqual(
            queryset.count(),
            3
        )
        self.assertIn(
            self.sp3,
            queryset
        )

    def test_filter_price_invalid_input(self):
        product_filter = ProductFilter(
            data={"price": "abc"},
            queryset=StoreProduct.objects.all()
        )

        self.assertFalse(
            product_filter.is_valid()
        )
        self.assertEqual(
            product_filter.qs.count(),
            3
        )

    def test_filter_price_empty_value(self):
        product_filter = ProductFilter(
            data={"price": ""},
            queryset=StoreProduct.objects.all()
        )

        self.assertTrue(
            product_filter.is_valid()
        )
        self.assertEqual(
            product_filter.qs.count(),
            3
        )

    def test_filter_price_zero(self):
        product = Product.objects.create(
            product_name="Zero Price",
            brand=self.brand,
            slug="zero-price"
        )

        product.product_group.add(
            self.group
        )

        store_product = StoreProduct.objects.create(
            store=self.store,
            product=product,
            price=0,
            is_active=True
        )

        product_filter = ProductFilter(
            data={"price": 0},
            queryset=StoreProduct.objects.all()
        )

        queryset = product_filter.qs

        self.assertEqual(
            queryset.count(),
            1
        )
        self.assertIn(
            store_product,
            queryset
        )