from django.core.exceptions import ValidationError

from apps.accounts.services import (
    validate_exists_mobile_number,
    validate_unique_email,
)
from apps.tests.base import BaseAccountTest


class ValidateExistsMobileNumberTests(BaseAccountTest):

    def test_mobile_number_exists(self):
        self.assertIsNone(
            validate_exists_mobile_number(
                self.user.mobile_number
            )
        )

    def test_mobile_number_not_exists(self):
        with self.assertRaises(ValidationError):
            validate_exists_mobile_number(
                "09129999999"
            )


class ValidateUniqueEmailTests(BaseAccountTest):

    def test_unique_email(self):
        self.assertIsNone(
            validate_unique_email(
                "new@test.com"
            )
        )

    def test_duplicate_email(self):
        with self.assertRaises(ValidationError):
            validate_unique_email(
                self.user.email
            )

    def test_duplicate_email_ignore_case(self):
        with self.assertRaises(ValidationError):
            validate_unique_email(
                "ALI@TEST.COM"
            )