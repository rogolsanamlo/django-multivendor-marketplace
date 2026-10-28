from datetime import timedelta

from django.utils import timezone

from apps.discounts.models import (
    DiscountBasket,
    DiscountBasketDetails,
)
from apps.discounts.services import get_price_by_discount
from apps.products.models import (
    Brand,
    Product,
    ProductGroup,
    StoreProduct,
)
from apps.tests.base import BaseAccountTest


class GetPriceByDiscountTest(BaseAccountTest):

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
            product_name="Test Product",
            brand=self.brand,
            slug="test-product",
            image_name=self.create_test_image(),
        )

        self.product.product_group.add(
            self.product_group
        )

        self.store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=100000,
        )

        self.now = timezone.now()

    def create_discount(
        self,
        discount,
        start_date,
        end_date,
        is_active=True,
    ):
        basket = DiscountBasket.objects.create(
            discount_title=f"Discount {discount}",
            start_date=start_date,
            end_date=end_date,
            discount=discount,
            is_active=is_active,
        )

        DiscountBasketDetails.objects.create(
            discount_basket=basket,
            store_product=self.store_product,
        )

        return basket

    def test_price_without_discount(self):
        price = get_price_by_discount(
            self.store_product
        )

        self.assertEqual(
            price,
            100000,
        )

    def test_price_with_active_discount(self):
        self.create_discount(
            discount=20,
            start_date=self.now - timedelta(days=1),
            end_date=self.now + timedelta(days=1),
        )

        price = get_price_by_discount(
            self.store_product
        )

        self.assertEqual(
            price,
            80000,
        )

    def test_only_maximum_active_discount_is_applied(self):
        self.create_discount(
            discount=10,
            start_date=self.now - timedelta(days=1),
            end_date=self.now + timedelta(days=1),
        )

        self.create_discount(
            discount=30,
            start_date=self.now - timedelta(days=1),
            end_date=self.now + timedelta(days=1),
        )

        self.create_discount(
            discount=20,
            start_date=self.now - timedelta(days=1),
            end_date=self.now + timedelta(days=1),
        )

        price = get_price_by_discount(
            self.store_product
        )

        self.assertEqual(
            price,
            70000,
        )

    def test_inactive_discount_is_ignored(self):
        self.create_discount(
            discount=50,
            start_date=self.now - timedelta(days=1),
            end_date=self.now + timedelta(days=1),
            is_active=False,
        )

        price = get_price_by_discount(
            self.store_product
        )

        self.assertEqual(
            price,
            100000,
        )

    def test_future_discount_is_ignored(self):
        self.create_discount(
            discount=50,
            start_date=self.now + timedelta(days=1),
            end_date=self.now + timedelta(days=2),
        )

        price = get_price_by_discount(
            self.store_product
        )

        self.assertEqual(
            price,
            100000,
        )

    def test_expired_discount_is_ignored(self):
        self.create_discount(
            discount=50,
            start_date=self.now - timedelta(days=2),
            end_date=self.now - timedelta(days=1),
        )

        price = get_price_by_discount(
            self.store_product
        )

        self.assertEqual(
            price,
            100000,
        )

    def test_discount_of_another_store_product_is_ignored(self):
        other_product = Product.objects.create(
            product_name="Other Product",
            brand=self.brand,
            slug="other-product",
            image_name=self.create_test_image(),
        )

        other_product.product_group.add(
            self.product_group
        )

        other_store_product = StoreProduct.objects.create(
            store=self.store,
            product=other_product,
            price=200000,
        )

        basket = DiscountBasket.objects.create(
            discount_title="Other Discount",
            start_date=self.now - timedelta(days=1),
            end_date=self.now + timedelta(days=1),
            discount=50,
            is_active=True,
        )

        DiscountBasketDetails.objects.create(
            discount_basket=basket,
            store_product=other_store_product,
        )

        price = get_price_by_discount(
            self.store_product
        )

        self.assertEqual(
            price,
            100000,
        )