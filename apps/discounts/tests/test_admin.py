from django.contrib import admin
from django.test import TestCase

from apps.discounts.admin import (
    CouponAdmin,
    DiscountBasketAdmin,
    DiscountBasketDetailsInline,
)
from apps.discounts.models import (
    Coupon,
    DiscountBasket,
    DiscountBasketDetails,
)


class DiscountAdminTest(TestCase):

    def test_coupon_is_registered_in_admin(self):
        self.assertIn(
            Coupon,
            admin.site._registry,
        )

        self.assertIsInstance(
            admin.site._registry[Coupon],
            CouponAdmin,
        )

    def test_discount_basket_is_registered_in_admin(self):
        self.assertIn(
            DiscountBasket,
            admin.site._registry,
        )

        self.assertIsInstance(
            admin.site._registry[DiscountBasket],
            DiscountBasketAdmin,
        )

    def test_discount_basket_details_is_not_registered_in_admin(self):
        self.assertNotIn(
            DiscountBasketDetails,
            admin.site._registry,
        )

    def test_coupon_admin_list_display(self):
        self.assertEqual(
            CouponAdmin.list_display,
            (
                "coupon_code",
                "start_date",
                "end_date",
                "discount",
                "is_active",
                "store",
            ),
        )

    def test_discount_basket_admin_list_display(self):
        self.assertEqual(
            DiscountBasketAdmin.list_display,
            (
                "discount_title",
                "start_date",
                "end_date",
                "discount",
                "is_active",
            ),
        )

    def test_discount_basket_admin_has_details_inline(self):
        self.assertEqual(
            DiscountBasketAdmin.inlines,
            [DiscountBasketDetailsInline],
        )

    def test_discount_basket_details_inline_model(self):
        self.assertEqual(
            DiscountBasketDetailsInline.model,
            DiscountBasketDetails,
        )

    def test_discount_basket_details_inline_extra(self):
        self.assertEqual(
            DiscountBasketDetailsInline.extra,
            3,
        )