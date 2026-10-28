from django.test import TestCase

from apps.discounts.forms import CouponForm


class CouponFormTest(TestCase):

    def test_coupon_form_with_valid_code(self):
        form = CouponForm(
            data={
                "coupon_code": "TEST10"
            }
        )

        self.assertTrue(form.is_valid())

    def test_coupon_form_without_coupon_code(self):
        form = CouponForm(
            data={
                "coupon_code": ""
            }
        )

        self.assertFalse(form.is_valid())

        self.assertIn(
            "coupon_code",
            form.errors
        )

    def test_coupon_form_has_coupon_code_field(self):
        form = CouponForm()

        self.assertIn(
            "coupon_code",
            form.fields
        )

    def test_coupon_code_widget_attributes(self):
        form = CouponForm()

        widget = form.fields["coupon_code"].widget

        self.assertEqual(
            widget.attrs["class"],
            "form-control"
        )

        self.assertEqual(
            widget.attrs["placeholder"],
            "کد تخفیف"
        )