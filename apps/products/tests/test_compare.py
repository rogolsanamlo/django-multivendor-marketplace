from django.test import RequestFactory, TestCase

from apps.accounts.models import CustomUser, Store
from apps.products.compare import CompareStoreProduct
from apps.products.models import (
    Brand,
    Product,
    ProductGroup,
    StoreProduct,
)


class BaseCompareTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.user = CustomUser.objects.create_user(
            mobile_number="09121112233",
            password="1234"
        )

        self.store = Store.objects.create(
            user=self.user,
            store_name="Digital Store",
            store_phone="09123334444",
            is_active=True
        )

        self.brand = Brand.objects.create(
            brand_title="Samsung",
            slug="samsung"
        )

        self.group = ProductGroup.objects.create(
            group_title="Mobile",
            slug="mobile",
            is_active=True
        )

        self.product = Product.objects.create(
            product_name="Galaxy S25",
            brand=self.brand,
            slug="galaxy-s25"
        )

        self.product.product_group.add(
            self.group
        )

        self.store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=10000000
        )

        self.request = self.factory.get("/")
        self.request.session = self.client.session

    def get_compare_store_product(self):
        return CompareStoreProduct(self.request)


class CompareStoreProductTests(BaseCompareTest):

    def test_init_create_empty_compare_store_list(self):
        compare = self.get_compare_store_product()

        self.assertEqual(
            compare.compare_store_product,
            []
        )
        self.assertEqual(
            compare.count,
            0
        )

    def test_init_existing_compare_store_list(self):
        self.request.session["compare_store_product"] = [
            self.store_product.id
        ]
        self.request.session.save()

        compare = self.get_compare_store_product()

        self.assertEqual(
            compare.compare_store_product,
            [self.store_product.id]
        )
        self.assertEqual(
            compare.count,
            1
        )

    def test_iter_returns_compare_store_products(self):
        self.request.session["compare_store_product"] = [
            self.store_product.id
        ]
        self.request.session.save()

        compare = self.get_compare_store_product()

        self.assertEqual(
            list(compare),
            [self.store_product.id]
        )

    def test_add_store_product(self):
        compare = self.get_compare_store_product()

        compare.add(
            self.store_product.id
        )

        self.assertIn(
            self.store_product.id,
            compare.compare_store_product
        )
        self.assertEqual(
            len(compare.compare_store_product),
            1
        )
        self.assertEqual(
            compare.count,
            1
        )

    def test_add_duplicate_store_product(self):
        compare = self.get_compare_store_product()

        compare.add(
            self.store_product.id
        )
        compare.add(
            self.store_product.id
        )

        self.assertEqual(
            len(compare.compare_store_product),
            1
        )
        self.assertEqual(
            compare.count,
            1
        )

    def test_remove_store_product(self):
        compare = self.get_compare_store_product()

        compare.add(
            self.store_product.id
        )
        compare.remove(
            self.store_product.id
        )

        self.assertEqual(
            compare.compare_store_product,
            []
        )
        self.assertEqual(
            compare.count,
            0
        )

    def test_remove_non_existing_store_product(self):
        compare = self.get_compare_store_product()

        compare.remove(
            self.store_product.id
        )

        self.assertEqual(
            compare.compare_store_product,
            []
        )
        self.assertEqual(
            compare.count,
            0
        )

    def test_clear_compare_store_product(self):
        compare = self.get_compare_store_product()

        compare.add(
            self.store_product.id
        )
        compare.clear()

        self.assertNotIn(
            "compare_store_product",
            self.request.session
        )
        self.assertEqual(
            compare.compare_store_product,
            []
        )
        self.assertEqual(
            compare.count,
            0
        )