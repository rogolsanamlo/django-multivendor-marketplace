from datetime import timedelta
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from PIL import Image

from apps.discounts.models import (
    Coupon,
    DiscountBasket,
    DiscountBasketDetails,
)
from apps.products.models import (
    Brand,
    Product,
    ProductGroup,
    StoreProduct,
)
from apps.tests.base import BaseAccountTest


class DiscountBaseTest(BaseAccountTest):

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

        self.start_date = timezone.now()

        self.end_date = (
            self.start_date
            + timedelta(days=7)
        )

    def create_test_image(self):

        image = Image.new(
            "RGB",
            (100, 100),
            "white",
        )

        image_io = BytesIO()

        image.save(
            image_io,
            format="JPEG",
        )

        image_io.seek(0)

        return SimpleUploadedFile(
            "test.jpg",
            image_io.read(),
            content_type="image/jpeg",
        )


class CouponModelTest(DiscountBaseTest):

    def setUp(self):

        super().setUp()

        self.coupon = Coupon.objects.create(
            store=self.store,
            coupon_code="TEST10",
            start_date=self.start_date,
            end_date=self.end_date,
            discount=10,
            is_active=True,
        )

    def test_coupon_store(self):

        self.assertEqual(
            self.coupon.store,
            self.store,
        )

    def test_coupon_code(self):

        self.assertEqual(
            self.coupon.coupon_code,
            "TEST10",
        )

    def test_coupon_start_date(self):

        self.assertEqual(
            self.coupon.start_date,
            self.start_date,
        )

    def test_coupon_end_date(self):

        self.assertEqual(
            self.coupon.end_date,
            self.end_date,
        )

    def test_coupon_discount(self):

        self.assertEqual(
            self.coupon.discount,
            10,
        )

    def test_coupon_is_active(self):

        self.assertTrue(
            self.coupon.is_active,
        )

    def test_coupon_str(self):

        self.assertEqual(
            str(self.coupon),
            "TEST10",
        )

    def test_delete_store_deletes_coupon(self):

        coupon_id = self.coupon.id

        self.store.delete()

        self.assertFalse(
            Coupon.objects.filter(
                id=coupon_id
            ).exists()
        )

    def test_coupon_discount_cannot_be_more_than_100(self):

        coupon = Coupon(
            store=self.store,
            coupon_code="TEST101",
            start_date=self.start_date,
            end_date=self.end_date,
            discount=101,
            is_active=True,
        )

        with self.assertRaises(ValidationError):
            coupon.full_clean()

    def test_coupon_discount_cannot_be_less_than_zero(self):

        coupon = Coupon(
            store=self.store,
            coupon_code="TEST-1",
            start_date=self.start_date,
            end_date=self.end_date,
            discount=-1,
            is_active=True,
        )

        with self.assertRaises(ValidationError):
            coupon.full_clean()

    def test_coupon_code_must_be_unique(self):

        duplicate_coupon = Coupon(
            store=self.store,
            coupon_code="TEST10",
            start_date=self.start_date,
            end_date=self.end_date,
            discount=20,
            is_active=True,
        )

        with self.assertRaises(ValidationError):
            duplicate_coupon.full_clean()


class DiscountBasketModelTest(DiscountBaseTest):

    def setUp(self):

        super().setUp()

        self.discount_basket = DiscountBasket.objects.create(
            discount_title="Summer Discount",
            start_date=self.start_date,
            end_date=self.end_date,
            discount=20,
            is_active=True,
        )

    def test_discount_basket_title(self):

        self.assertEqual(
            self.discount_basket.discount_title,
            "Summer Discount",
        )

    def test_discount_basket_start_date(self):

        self.assertEqual(
            self.discount_basket.start_date,
            self.start_date,
        )

    def test_discount_basket_end_date(self):

        self.assertEqual(
            self.discount_basket.end_date,
            self.end_date,
        )

    def test_discount_basket_discount(self):

        self.assertEqual(
            self.discount_basket.discount,
            20,
        )

    def test_discount_basket_is_active(self):

        self.assertTrue(
            self.discount_basket.is_active,
        )

    def test_discount_basket_str(self):

        self.assertEqual(
            str(self.discount_basket),
            "Summer Discount",
        )

    def test_discount_basket_discount_cannot_be_more_than_100(self):

        discount_basket = DiscountBasket(
            discount_title="Invalid Discount",
            start_date=self.start_date,
            end_date=self.end_date,
            discount=101,
            is_active=True,
        )

        with self.assertRaises(ValidationError):
            discount_basket.full_clean()

    def test_discount_basket_discount_cannot_be_less_than_zero(self):

        discount_basket = DiscountBasket(
            discount_title="Invalid Discount",
            start_date=self.start_date,
            end_date=self.end_date,
            discount=-1,
            is_active=True,
        )

        with self.assertRaises(ValidationError):
            discount_basket.full_clean()


class DiscountBasketDetailsModelTest(DiscountBaseTest):

    def setUp(self):

        super().setUp()

        self.discount_basket = DiscountBasket.objects.create(
            discount_title="Summer Discount",
            start_date=self.start_date,
            end_date=self.end_date,
            discount=20,
            is_active=True,
        )

        self.discount_details = DiscountBasketDetails.objects.create(
            discount_basket=self.discount_basket,
            store_product=self.store_product,
        )

    def test_discount_basket(self):

        self.assertEqual(
            self.discount_details.discount_basket,
            self.discount_basket,
        )

    def test_store_product(self):

        self.assertEqual(
            self.discount_details.store_product,
            self.store_product,
        )

    def test_store_product_can_access_discounts(self):

        discount = (
            self.store_product.discounts.first()
        )

        self.assertEqual(
            discount,
            self.discount_details,
        )

    def test_discount_basket_can_access_details(self):

        details = (
            self.discount_basket
            .discountbasketdetails_set
            .first()
        )

        self.assertEqual(
            details,
            self.discount_details,
        )

    def test_delete_discount_basket_deletes_details(self):

        details_id = self.discount_details.id

        self.discount_basket.delete()

        self.assertFalse(
            DiscountBasketDetails.objects.filter(
                id=details_id
            ).exists()
        )

    def test_delete_store_product_deletes_details(self):

        details_id = self.discount_details.id

        self.store_product.delete()

        self.assertFalse(
            DiscountBasketDetails.objects.filter(
                id=details_id
            ).exists()
        )

    def test_same_product_cannot_be_added_twice_to_same_basket(self):

        duplicate_details = DiscountBasketDetails(
            discount_basket=self.discount_basket,
            store_product=self.store_product,
        )

        with self.assertRaises(ValidationError):
            duplicate_details.full_clean()