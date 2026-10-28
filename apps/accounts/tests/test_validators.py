from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from apps.accounts.validators import (
    validate_image,
    validate_password_strength,
    validate_passwords,
    validate_phone,
)
from apps.tests.base import BaseAccountTest


class ValidatePasswordStrengthTests(TestCase):

    def test_valid_password(self):
        self.assertIsNone(
            validate_password_strength("Test@123")
        )

    def test_password_too_short(self):
        with self.assertRaises(ValidationError):
            validate_password_strength("Tes@12")

    def test_password_without_number(self):
        with self.assertRaises(ValidationError):
            validate_password_strength("Test@Test")

    def test_password_without_uppercase(self):
        with self.assertRaises(ValidationError):
            validate_password_strength("test@123")

    def test_password_without_special_character(self):
        with self.assertRaises(ValidationError):
            validate_password_strength("Test1234")

    def test_password_with_invalid_character(self):
        with self.assertRaises(ValidationError):
            validate_password_strength("Test@123✓")


class ValidatePhoneTests(TestCase):

    def test_valid_mobile_number(self):
        self.assertIsNone(
            validate_phone("09123456789", "mobile")
        )

    def test_valid_store_phone(self):
        self.assertIsNone(
            validate_phone("02112345678", "store")
        )

    def test_mobile_number_without_09(self):
        with self.assertRaises(ValidationError):
            validate_phone("08123456789", "mobile")

    def test_mobile_number_too_short(self):
        with self.assertRaises(ValidationError):
            validate_phone("0912345678", "mobile")

    def test_mobile_number_too_long(self):
        with self.assertRaises(ValidationError):
            validate_phone("091234567890", "mobile")

    def test_mobile_number_contains_letters(self):
        with self.assertRaises(ValidationError):
            validate_phone("09123abc789", "mobile")

    def test_store_phone_without_zero(self):
        with self.assertRaises(ValidationError):
            validate_phone("2112345678", "store")

    def test_store_phone_too_short(self):
        with self.assertRaises(ValidationError):
            validate_phone("0211234567", "store")

    def test_store_phone_too_long(self):
        with self.assertRaises(ValidationError):
            validate_phone("021123456789", "store")

    def test_store_phone_contains_letters(self):
        with self.assertRaises(ValidationError):
            validate_phone("02112ab5678", "store")

    def test_invalid_phone_type(self):
        with self.assertRaises(ValidationError):
            validate_phone("09123456789", "invalid")


class ValidatePasswordsTests(TestCase):

    def test_valid_passwords(self):
        self.assertIsNone(
            validate_passwords(
                "Test@123",
                "Test@123"
            )
        )

    def test_password1_is_empty(self):
        with self.assertRaises(ValidationError):
            validate_passwords(
                "",
                "Test@123"
            )

    def test_password2_is_empty(self):
        with self.assertRaises(ValidationError):
            validate_passwords(
                "Test@123",
                ""
            )

    def test_passwords_do_not_match(self):
        with self.assertRaises(ValidationError):
            validate_passwords(
                "Test@123",
                "Test@1234"
            )


class ValidateImageTests(BaseAccountTest):

    def create_test_image(
        self,
        name="test.jpg",
        size=(100, 100),
        image_format="JPEG"
    ):
        file = BytesIO()

        image = Image.new(
            "RGB",
            size=size,
            color="red"
        )

        image.save(
            file,
            format=image_format
        )

        file.seek(0)

        return SimpleUploadedFile(
            name=name,
            content=file.read(),
            content_type="image/jpeg"
        )

    def test_valid_image(self):
        image = self.create_test_image()

        self.assertEqual(
            validate_image(image),
            image
        )

    def test_none_image(self):
        self.assertIsNone(
            validate_image(None)
        )

    def test_invalid_extension(self):
        image = self.create_test_image(
            name="test.pdf"
        )

        with self.assertRaises(ValidationError):
            validate_image(image)

    def test_large_image(self):
        oversized_content = b"x" * (1024 * 1024 + 1)

        image = SimpleUploadedFile(
            "large.jpg",
            oversized_content,
            content_type="image/jpeg"
        )

        with self.assertRaises(ValidationError):
            validate_image(image)

    def test_invalid_image_file(self):
        image = SimpleUploadedFile(
            "test.jpg",
            b"this is not image",
            content_type="image/jpeg"
        )

        with self.assertRaises(ValidationError):
            validate_image(image)