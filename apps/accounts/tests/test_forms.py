from io import BytesIO
from unittest.mock import patch

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from apps.accounts.forms import (
    ChangePasswordForm,
    CreateStoreForm,
    EditStoreForm,
    ImageValidationMixin,
    LoginUserForm,
    RegisterUserForm,
    RememberPasswordForm,
    StoreFormWidgetMixin,
    UpdateProfileForm,
    UpdateUserProfileForm,
    UserChangeForm,
    UserCreationForm,
    VerifyRegisterForm,
)
from apps.accounts.models import CustomUser, Store


def create_test_image():
    image = Image.new("RGB", (1, 1), color="red")
    buffer = BytesIO()
    image.save(buffer, format="JPEG")

    return SimpleUploadedFile(
        "test.jpg",
        buffer.getvalue(),
        content_type="image/jpeg",
    )


class BaseAccountTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            mobile_number="09120000000",
            password="123456",
            name="Ali",
            family="Ahmadi",
            email="ali@test.com",
        )

        self.profile = self.user.userprofile

        self.image = create_test_image()

        self.store = Store.objects.create(
            user=self.user,
            store_name="Digital Shop",
            store_phone="09121111111",
        )


class UserCreationFormTests(BaseAccountTest):

    def test_valid_form(self):
        form = UserCreationForm(
            data={
                "mobile_number": "09123333333",
                "email": "new@test.com",
                "name": "Reza",
                "family": "Ahmadi",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )

        self.assertTrue(form.is_valid())

    def test_invalid_mobile(self):
        form = UserCreationForm(
            data={
                "mobile_number": "123",
                "email": "new@test.com",
                "name": "Reza",
                "family": "Ahmadi",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("mobile_number", form.errors)

    def test_duplicate_email(self):
        form = UserCreationForm(
            data={
                "mobile_number": "09123333333",
                "email": "ALI@TEST.COM",
                "name": "Reza",
                "family": "Ahmadi",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_mismatched_passwords(self):
        form = UserCreationForm(
            data={
                "mobile_number": "09123333333",
                "email": "new@test.com",
                "name": "Reza",
                "family": "Ahmadi",
                "password1": "StrongPass123!",
                "password2": "DifferentPass123!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_weak_password(self):
        form = UserCreationForm(
            data={
                "mobile_number": "09123333333",
                "email": "new@test.com",
                "name": "Reza",
                "family": "Ahmadi",
                "password1": "123",
                "password2": "123",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_save_hashes_password(self):
        form = UserCreationForm(
            data={
                "mobile_number": "09123333333",
                "email": "new@test.com",
                "name": "Reza",
                "family": "Ahmadi",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )

        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertNotEqual(user.password, "StrongPass123!")
        self.assertTrue(user.check_password("StrongPass123!"))


class UserChangeFormTests(BaseAccountTest):

    def test_valid_form(self):
        form = UserChangeForm(
            instance=self.user,
            data={
                "mobile_number": self.user.mobile_number,
                "password": self.user.password,
                "email": self.user.email,
                "name": self.user.name,
                "family": self.user.family,
                "is_active": self.user.is_active,
                "is_admin": self.user.is_admin,
            },
        )

        self.assertTrue(form.is_valid())

    def test_password_is_read_only_password_hash_field(self):
        self.assertIsInstance(
            UserChangeForm.base_fields["password"],
            ReadOnlyPasswordHashField,
        )

    def test_password_help_text(self):
        field = UserChangeForm.base_fields["password"]

        self.assertIn(
            "برای تغییر رمز عبور",
            field.help_text,
        )

    def test_exact_fields(self):
        expected_fields = [
            "mobile_number",
            "password",
            "email",
            "name",
            "family",
            "is_active",
            "is_admin",
        ]

        self.assertEqual(
            list(UserChangeForm.base_fields.keys()),
            expected_fields,
        )


class RegisterUserFormTests(BaseAccountTest):

    def test_valid_form(self):
        form = RegisterUserForm(
            data={
                "mobile_number": "09123333333",
                "name": "Reza",
                "family": "Ahmadi",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )

        self.assertTrue(form.is_valid())

    def test_invalid_mobile(self):
        form = RegisterUserForm(
            data={
                "mobile_number": "123",
                "name": "Reza",
                "family": "Ahmadi",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("mobile_number", form.errors)

    def test_mismatched_passwords(self):
        form = RegisterUserForm(
            data={
                "mobile_number": "09123333333",
                "name": "Reza",
                "family": "Ahmadi",
                "password1": "StrongPass123!",
                "password2": "DifferentPass123!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_weak_password(self):
        form = RegisterUserForm(
            data={
                "mobile_number": "09123333333",
                "name": "Reza",
                "family": "Ahmadi",
                "password1": "123",
                "password2": "123",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_save_hashes_password(self):
        form = RegisterUserForm(
            data={
                "mobile_number": "09123333333",
                "name": "Reza",
                "family": "Ahmadi",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )

        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertNotEqual(user.password, "StrongPass123!")
        self.assertTrue(user.check_password("StrongPass123!"))

    def test_exact_fields(self):
        expected_fields = [
            "mobile_number",
            "name",
            "family",
            "password1",
            "password2",
        ]

        self.assertEqual(
            list(RegisterUserForm.base_fields.keys()),
            expected_fields,
        )

    def test_password_widgets(self):
        self.assertIsInstance(
            RegisterUserForm.base_fields["password1"].widget,
            forms.PasswordInput,
        )

        self.assertIsInstance(
            RegisterUserForm.base_fields["password2"].widget,
            forms.PasswordInput,
        )


class VerifyRegisterFormTests(TestCase):

    def test_valid_form(self):
        form = VerifyRegisterForm(
            data={
                "active_code": "123456",
            }
        )

        self.assertTrue(form.is_valid())

    def test_active_code_required(self):
        form = VerifyRegisterForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn("active_code", form.errors)

    def test_active_code_required_message(self):
        form = VerifyRegisterForm(data={})

        self.assertFalse(form.is_valid())

        self.assertEqual(
            form.errors["active_code"][0],
            "این فیلد نمی تواند خالی باشد",
        )

    def test_exact_fields(self):
        self.assertEqual(
            list(VerifyRegisterForm.base_fields.keys()),
            ["active_code"],
        )

    def test_widget(self):
        field = VerifyRegisterForm.base_fields["active_code"]

        self.assertIsInstance(
            field.widget,
            forms.TextInput,
        )

        self.assertEqual(
            field.widget.attrs["class"],
            "form-control",
        )


class LoginUserFormTests(TestCase):

    def test_valid_form(self):
        form = LoginUserForm(
            data={
                "mobile_number": "09120000000",
                "password": "123456",
            }
        )

        self.assertTrue(form.is_valid())

    def test_invalid_mobile(self):
        form = LoginUserForm(
            data={
                "mobile_number": "123",
                "password": "123456",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("mobile_number", form.errors)

    def test_mobile_required(self):
        form = LoginUserForm(
            data={
                "password": "123456",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("mobile_number", form.errors)

    def test_password_required(self):
        form = LoginUserForm(
            data={
                "mobile_number": "09120000000",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)

    def test_required_error_messages(self):
        form = LoginUserForm(data={})

        self.assertFalse(form.is_valid())

        self.assertEqual(
            form.errors["mobile_number"][0],
            "این فیلد نمی تواند خالی باشد",
        )

        self.assertEqual(
            form.errors["password"][0],
            "این فیلد نمی تواند خالی باشد",
        )

    def test_exact_fields(self):
        expected_fields = [
            "mobile_number",
            "password",
        ]

        self.assertEqual(
            list(LoginUserForm.base_fields.keys()),
            expected_fields,
        )

    def test_widgets(self):
        self.assertIsInstance(
            LoginUserForm.base_fields["mobile_number"].widget,
            forms.TextInput,
        )

        self.assertIsInstance(
            LoginUserForm.base_fields["password"].widget,
            forms.PasswordInput,
        )


class ChangePasswordFormTests(TestCase):

    def test_valid_form(self):
        form = ChangePasswordForm(
            data={
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )

        self.assertTrue(form.is_valid())

    def test_mismatched_passwords(self):
        form = ChangePasswordForm(
            data={
                "password1": "StrongPass123!",
                "password2": "DifferentPass123!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_weak_password(self):
        form = ChangePasswordForm(
            data={
                "password1": "123",
                "password2": "123",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_exact_fields(self):
        self.assertEqual(
            list(ChangePasswordForm.base_fields.keys()),
            ["password1", "password2"],
        )

    def test_widgets(self):
        self.assertIsInstance(
            ChangePasswordForm.base_fields["password1"].widget,
            forms.PasswordInput,
        )

        self.assertIsInstance(
            ChangePasswordForm.base_fields["password2"].widget,
            forms.PasswordInput,
        )

    def test_required_error_messages(self):
        form = ChangePasswordForm(data={})

        self.assertFalse(form.is_valid())

        self.assertEqual(
            form.errors["password1"][0],
            "این فیلد نمی تواند خالی باشد",
        )

        self.assertEqual(
            form.errors["password2"][0],
            "این فیلد نمی تواند خالی باشد",
        )


class RememberPasswordFormTests(BaseAccountTest):

    def test_valid_existing_mobile(self):
        form = RememberPasswordForm(
            data={
                "mobile_number": self.user.mobile_number,
            }
        )

        self.assertTrue(form.is_valid())

    def test_mobile_required(self):
        form = RememberPasswordForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn("mobile_number", form.errors)

    def test_invalid_mobile(self):
        form = RememberPasswordForm(
            data={
                "mobile_number": "123",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("mobile_number", form.errors)

    def test_nonexistent_mobile(self):
        form = RememberPasswordForm(
            data={
                "mobile_number": "09123333333",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("mobile_number", form.errors)

    def test_required_error_message(self):
        form = RememberPasswordForm(data={})

        self.assertFalse(form.is_valid())

        self.assertEqual(
            form.errors["mobile_number"][0],
            "شماره موبایل الزامی است",
        )

    def test_exact_fields(self):
        self.assertEqual(
            list(RememberPasswordForm.base_fields.keys()),
            ["mobile_number"],
        )

    def test_widget(self):
        field = RememberPasswordForm.base_fields["mobile_number"]

        self.assertIsInstance(
            field.widget,
            forms.TextInput,
        )

        self.assertEqual(
            field.widget.attrs["class"],
            "form-control",
        )


class ImageValidationMixinTests(TestCase):

    def test_returns_image(self):
        image = create_test_image()
        mixin = ImageValidationMixin()

        self.assertIs(
            mixin.validate_uploaded_image(image),
            image,
        )

    def test_none_stays_none(self):
        mixin = ImageValidationMixin()

        self.assertIsNone(
            mixin.validate_uploaded_image(None)
        )

    @patch("apps.accounts.forms.validate_image")
    def test_validate_image_called(self, mock_validate):
        image = create_test_image()
        mixin = ImageValidationMixin()

        result = mixin.validate_uploaded_image(image)

        mock_validate.assert_called_once_with(image)
        self.assertIs(result, image)

    @patch("apps.accounts.forms.validate_image")
    def test_validate_image_error_is_raised(self, mock_validate):
        mock_validate.side_effect = ValidationError(
            "تصویر نامعتبر است"
        )

        image = create_test_image()
        mixin = ImageValidationMixin()

        with self.assertRaises(ValidationError):
            mixin.validate_uploaded_image(image)


class StoreFormWidgetMixinTests(TestCase):

    def test_widget_types(self):
        widgets = StoreFormWidgetMixin.store_widgets

        self.assertIsInstance(
            widgets["store_name"],
            forms.TextInput,
        )

        self.assertIsInstance(
            widgets["store_phone"],
            forms.TextInput,
        )

        self.assertIsInstance(
            widgets["address"],
            forms.Textarea,
        )

        self.assertIsInstance(
            widgets["description"],
            forms.Textarea,
        )

        self.assertIsInstance(
            widgets["logo"],
            forms.FileInput,
        )

    def test_placeholders(self):
        widgets = StoreFormWidgetMixin.store_widgets

        self.assertEqual(
            widgets["store_name"].attrs["placeholder"],
            "نام فروشگاه",
        )

        self.assertEqual(
            widgets["store_phone"].attrs["placeholder"],
            "شماره فروشگاه",
        )

        self.assertEqual(
            widgets["address"].attrs["placeholder"],
            "آدرس فروشگاه",
        )

        self.assertEqual(
            widgets["description"].attrs["placeholder"],
            "توضیحات فروشگاه",
        )

    def test_textarea_rows(self):
        widgets = StoreFormWidgetMixin.store_widgets

        self.assertEqual(
            widgets["address"].attrs["rows"],
            3,
        )

        self.assertEqual(
            widgets["description"].attrs["rows"],
            4,
        )


class CreateStoreFormTests(BaseAccountTest):

    def test_valid_form_with_logo(self):
        form = CreateStoreForm(
            data={
                "store_name": "New Shop",
                "store_phone": "09122222222",
                "address": "Tehran",
                "description": "Digital products",
            },
            files={
                "logo": self.image,
            },
        )

        self.assertTrue(form.is_valid())

    def test_valid_form_without_logo(self):
        form = CreateStoreForm(
            data={
                "store_name": "New Shop",
                "store_phone": "09122222222",
                "address": "Tehran",
                "description": "Digital products",
            }
        )

        self.assertTrue(form.is_valid())

    def test_invalid_store_phone(self):
        form = CreateStoreForm(
            data={
                "store_name": "New Shop",
                "store_phone": "123",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("store_phone", form.errors)

    def test_duplicate_store_phone(self):
        form = CreateStoreForm(
            data={
                "store_name": "New Shop",
                "store_phone": self.store.store_phone,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("store_phone", form.errors)

    @patch("apps.accounts.forms.validate_image")
    def test_logo_validation(self, mock_validate):
        form = CreateStoreForm(
            data={
                "store_name": "New Shop",
                "store_phone": "09122222222",
            },
            files={
                "logo": self.image,
            },
        )

        self.assertTrue(form.is_valid())

        mock_validate.assert_called_once_with(
            form.cleaned_data["logo"]
        )

    @patch("apps.accounts.forms.validate_image")
    def test_invalid_logo(self, mock_validate):
        mock_validate.side_effect = ValidationError(
            "تصویر نامعتبر است"
        )

        form = CreateStoreForm(
            data={
                "store_name": "New Shop",
                "store_phone": "09122222222",
            },
            files={
                "logo": self.image,
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("logo", form.errors)

    def test_widgets(self):
        self.assertIsInstance(
            CreateStoreForm.base_fields["store_name"].widget,
            forms.TextInput,
        )

        self.assertIsInstance(
            CreateStoreForm.base_fields["store_phone"].widget,
            forms.TextInput,
        )

        self.assertIsInstance(
            CreateStoreForm.base_fields["address"].widget,
            forms.Textarea,
        )

        self.assertIsInstance(
            CreateStoreForm.base_fields["description"].widget,
            forms.Textarea,
        )

        self.assertIsInstance(
            CreateStoreForm.base_fields["logo"].widget,
            forms.FileInput,
        )

    def test_exact_fields(self):
        expected_fields = [
            "store_name",
            "store_phone",
            "address",
            "description",
            "logo",
        ]

        self.assertEqual(
            list(CreateStoreForm.base_fields.keys()),
            expected_fields,
        )

    def test_store_phone_required(self):
        form = CreateStoreForm(
            data={
                "store_name": "New Shop",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("store_phone", form.errors)


class EditStoreFormTests(BaseAccountTest):

    def test_valid_form(self):
        form = EditStoreForm(
            instance=self.store,
            data={
                "store_name": "Updated Shop",
                "store_phone": "09122222222",
                "address": "Tehran",
                "description": "Updated description",
            },
        )

        self.assertTrue(form.is_valid())

    def test_invalid_store_phone(self):
        form = EditStoreForm(
            instance=self.store,
            data={
                "store_name": "Updated Shop",
                "store_phone": "123",
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("store_phone", form.errors)

    def test_duplicate_store_phone(self):
        Store.objects.create(
            user=CustomUser.objects.create_user(
                mobile_number="09123333334",
                password="123456",
            ),
            store_name="Other Shop",
            store_phone="09124444444",
        )

        form = EditStoreForm(
            instance=self.store,
            data={
                "store_name": "Updated Shop",
                "store_phone": "09124444444",
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("store_phone", form.errors)

    def test_same_phone_for_same_store(self):
        form = EditStoreForm(
            instance=self.store,
            data={
                "store_name": self.store.store_name,
                "store_phone": self.store.store_phone,
            },
        )

        self.assertTrue(form.is_valid())

    @patch("apps.accounts.forms.validate_image")
    def test_logo_validation(self, mock_validate):
        form = EditStoreForm(
            instance=self.store,
            data={
                "store_name": self.store.store_name,
                "store_phone": self.store.store_phone,
            },
            files={
                "logo": self.image,
            },
        )

        self.assertTrue(form.is_valid())

        mock_validate.assert_called_once_with(
            form.cleaned_data["logo"]
        )

    @patch("apps.accounts.forms.validate_image")
    def test_invalid_logo(self, mock_validate):
        mock_validate.side_effect = ValidationError(
            "تصویر نامعتبر است"
        )

        form = EditStoreForm(
            instance=self.store,
            data={
                "store_name": self.store.store_name,
                "store_phone": self.store.store_phone,
            },
            files={
                "logo": self.image,
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("logo", form.errors)

    def test_exact_fields(self):
        expected_fields = [
            "store_name",
            "store_phone",
            "address",
            "description",
            "logo",
        ]

        self.assertEqual(
            list(EditStoreForm.base_fields.keys()),
            expected_fields,
        )


class UpdateProfileFormTests(BaseAccountTest):

    def test_valid_form(self):
        form = UpdateProfileForm(
            instance=self.user,
            data={
                "name": "Reza",
                "family": "Ahmadi",
                "email": "reza@test.com",
            },
        )

        self.assertTrue(form.is_valid())

    def test_duplicate_email(self):
        CustomUser.objects.create_user(
            mobile_number="09123333333",
            password="123456",
            email="other@test.com",
        )

        form = UpdateProfileForm(
            instance=self.user,
            data={
                "name": "Reza",
                "family": "Ahmadi",
                "email": "OTHER@TEST.COM",
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_same_email(self):
        form = UpdateProfileForm(
            instance=self.user,
            data={
                "name": self.user.name,
                "family": self.user.family,
                "email": self.user.email,
            },
        )

        self.assertTrue(form.is_valid())

    def test_exact_fields(self):
        expected_fields = [
            "name",
            "family",
            "email",
        ]

        self.assertEqual(
            list(UpdateProfileForm.base_fields.keys()),
            expected_fields,
        )

    def test_widgets(self):
        self.assertIsInstance(
            UpdateProfileForm.base_fields["name"].widget,
            forms.TextInput,
        )

        self.assertIsInstance(
            UpdateProfileForm.base_fields["family"].widget,
            forms.TextInput,
        )

        self.assertIsInstance(
            UpdateProfileForm.base_fields["email"].widget,
            forms.EmailInput,
        )

    def test_name_not_required(self):
        form = UpdateProfileForm(
            instance=self.user,
            data={
                "name": "",
                "family": "Ahmadi",
                "email": "new@test.com",
            },
        )

        self.assertTrue(form.is_valid())

    def test_family_not_required(self):
        form = UpdateProfileForm(
            instance=self.user,
            data={
                "name": "Ali",
                "family": "",
                "email": "new@test.com",
            },
        )

        self.assertTrue(form.is_valid())


class UpdateUserProfileFormTests(BaseAccountTest):

    def test_valid_form(self):
        form = UpdateUserProfileForm(
            instance=self.profile,
            data={
                "address": "Tehran",
            },
        )

        self.assertTrue(form.is_valid())

    def test_update_address(self):
        form = UpdateUserProfileForm(
            instance=self.profile,
            data={
                "address": "Urmia",
            },
        )

        self.assertTrue(form.is_valid())

        profile = form.save()

        self.assertEqual(
            profile.address,
            "Urmia",
        )

    @patch("apps.accounts.forms.validate_image")
    def test_image_validation(self, mock_validate):
        form = UpdateUserProfileForm(
            instance=self.profile,
            data={
                "address": "Tehran",
            },
            files={
                "image_name": self.image,
            },
        )

        self.assertTrue(form.is_valid())

        mock_validate.assert_called_once_with(
            form.cleaned_data["image_name"]
        )

    @patch("apps.accounts.forms.validate_image")
    def test_invalid_image(self, mock_validate):
        mock_validate.side_effect = ValidationError(
            "تصویر نامعتبر است"
        )

        form = UpdateUserProfileForm(
            instance=self.profile,
            data={
                "address": "Tehran",
            },
            files={
                "image_name": self.image,
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("image_name", form.errors)

    def test_exact_fields(self):
        expected_fields = [
            "address",
            "image_name",
        ]

        self.assertEqual(
            list(UpdateUserProfileForm.base_fields.keys()),
            expected_fields,
        )

    def test_widgets(self):
        self.assertIsInstance(
            UpdateUserProfileForm.base_fields["address"].widget,
            forms.Textarea,
        )

        self.assertIsInstance(
            UpdateUserProfileForm.base_fields["image_name"].widget,
            forms.FileInput,
        )

    def test_address_rows(self):
        self.assertEqual(
            UpdateUserProfileForm.base_fields[
                "address"
            ].widget.attrs["rows"],
            3,
        )