from django.test import TestCase

from apps.orders.forms import OrderForm
from apps.orders.models import PaymentType

class OrderFormTests(TestCase):

    def setUp(self):

        self.payment = PaymentType.objects.create(
            payment_title="Online"
        )

    def test_valid_form(self):

            form = OrderForm(
                data={
                    "name": "Ali",
                    "family": "Ahmadi",
                    "email": "a@test.com",
                    "phone_number": "09120000000",
                    "address": "Tehran",
                    "description": "test",
                    "payment_type": self.payment.id,
                }
            )

            self.assertTrue(form.is_valid())
from django.test import TestCase

from apps.orders.forms import OrderForm
from apps.orders.models import PaymentType


class OrderFormTests(TestCase):

    def setUp(self):
        self.payment = PaymentType.objects.create(
            payment_title="Online",
        )

    def test_valid_form(self):
        form = OrderForm(
            data={
                "name": "Ali",
                "family": "Ahmadi",
                "email": "a@test.com",
                "phone_number": "09120000000",
                "address": "Tehran",
                "description": "test",
                "payment_type": self.payment.id,
            }
        )

        self.assertTrue(
            form.is_valid()
        )

    def test_name_required(self):
        form = OrderForm(
            data={
                "family": "Ahmadi",
                "address": "Tehran",
                "payment_type": self.payment.id,
            }
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "name",
            form.errors,
        )

    def test_family_required(self):
        form = OrderForm(
            data={
                "name": "Ali",
                "address": "Tehran",
                "payment_type": self.payment.id,
            }
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "family",
            form.errors,
        )

    def test_address_required(self):
        form = OrderForm(
            data={
                "name": "Ali",
                "family": "Ahmadi",
                "payment_type": self.payment.id,
            }
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "address",
            form.errors,
        )

    def test_payment_type_required(self):
        form = OrderForm(
            data={
                "name": "Ali",
                "family": "Ahmadi",
                "address": "Tehran",
            }
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "payment_type",
            form.errors,
        )
    def test_name_required(self):

            form = OrderForm(
                data={
                    "family": "Ahmadi",
                    "address": "Tehran",
                    "payment_type": self.payment.id,
                }
            )

            self.assertFalse(form.is_valid())

            self.assertIn(
                "name",
                form.errors
            )

    def test_family_required(self):

            form = OrderForm(
                data={
                    "name": "Ali",
                    "address": "Tehran",
                    "payment_type": self.payment.id,
                }
            )

            self.assertFalse(form.is_valid())

            self.assertIn(
                "family",
                form.errors
            )

    def test_address_required(self):

            form = OrderForm(
                data={
                    "name": "Ali",
                    "family": "Ahmadi",
                    "payment_type": self.payment.id,
                }
            )

            self.assertFalse(form.is_valid())

            self.assertIn(
                "address",
                form.errors
            )

    def test_payment_type_required(self):

            form = OrderForm(
                data={
                    "name": "Ali",
                    "family": "Ahmadi",
                    "address": "Tehran",
                }
            )

            self.assertFalse(form.is_valid())

            self.assertIn(
                "payment_type",
                form.errors
            )