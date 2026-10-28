from unittest.mock import patch

from django.contrib.messages import get_messages
from django.urls import reverse

from apps.accounts.forms import (
    ChangePasswordForm,
    CreateStoreForm,
    EditStoreForm,
    LoginUserForm,
    RegisterUserForm,
    RememberPasswordForm,
    UpdateProfileForm,
    UpdateUserProfileForm,
    VerifyRegisterForm,
)
from apps.accounts.models import CustomUser, Store, UserProfile
from apps.orders.models import Order
from apps.payments.models import Payment

from apps.tests.base import BaseAccountTest


class RegisterUserViewTests(BaseAccountTest):
    def setUp(self):
        super().setUp()
        self.activate_user()

    def test_get_register_page(self):
        response = self.client.get(
            reverse("accounts:register")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/register.html"
        )

    def test_get_register_page_authenticated_user(self):
        self.activate_user()
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("accounts:register")
        )

        self.assertRedirects(
            response,
            reverse("main:index")
        )

    def test_get_uses_register_form(self):
        response = self.client.get(
            reverse("accounts:register")
        )

        self.assertIn(
            "form",
            response.context
        )

        self.assertIsInstance(
            response.context["form"],
            RegisterUserForm
        )

    @patch("apps.accounts.views.utils.send_sms")
    @patch("apps.accounts.views.utils.create_random_code")
    def test_post_valid_data_create_user(
        self,
        mock_create_random_code,
        mock_send_sms,
    ):
        mock_create_random_code.return_value = "12345"

        response = self.client.post(
            reverse("accounts:register"),
            data={
                "mobile_number": "09125556666",
                "name": "Ali",
                "family": "Ahmadi",
                "password1": "Test@12345",
                "password2": "Test@12345",
            }
        )

        self.assertRedirects(
            response,
            reverse("accounts:verify")
        )

        user = CustomUser.objects.get(
            mobile_number="09125556666"
        )

        self.assertEqual(
            user.name,
            "Ali"
        )

        self.assertEqual(
            user.family,
            "Ahmadi"
        )

        self.assertTrue(
            user.check_password("Test@12345")
        )

        self.assertFalse(
            user.is_active
        )

        self.assertEqual(
            user.active_code,
            "12345"
        )

    @patch("apps.accounts.views.utils.send_sms")
    @patch("apps.accounts.views.utils.create_random_code")
    def test_post_valid_data_send_sms(
        self,
        mock_create_random_code,
        mock_send_sms,
    ):
        mock_create_random_code.return_value = "12345"

        self.client.post(
            reverse("accounts:register"),
            data={
                "mobile_number": "09125556666",
                "name": "Ali",
                "family": "Ahmadi",
                "password1": "Test@12345",
                "password2": "Test@12345",
            }
        )

        mock_send_sms.assert_called_once_with(
            "09125556666",
            "12345"
        )

    @patch("apps.accounts.views.utils.send_sms")
    @patch("apps.accounts.views.utils.create_random_code")
    def test_post_valid_data_create_session(
        self,
        mock_create_random_code,
        mock_send_sms,
    ):
        mock_create_random_code.return_value = "12345"

        self.client.post(
            reverse("accounts:register"),
            data={
                "mobile_number": "09125556666",
                "name": "Ali",
                "family": "Ahmadi",
                "password1": "Test@12345",
                "password2": "Test@12345",
            }
        )

        session = self.client.session["user_session"]

        self.assertEqual(
            session["mobile_number"],
            "09125556666"
        )

        self.assertEqual(
            session["active_code"],
            "12345"
        )

        self.assertFalse(
            session["remember_password"]
        )

    def test_post_invalid_data_return_form(self):
        response = self.client.post(
            reverse("accounts:register"),
            data={
                "mobile_number": "0912",
                "name": "Ali",
                "family": "Ahmadi",
                "password1": "123",
                "password2": "1234",
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/register.html"
        )

        self.assertFalse(
            response.context["form"].is_valid()
        )

    @patch("apps.accounts.views.utils.send_sms")
    @patch("apps.accounts.views.utils.create_random_code")
    def test_post_send_sms_exception(
        self,
        mock_create_random_code,
        mock_send_sms,
    ):
        mock_create_random_code.return_value = "12345"
        mock_send_sms.side_effect = Exception("SMS Error")

        response = self.client.post(
            reverse("accounts:register"),
            data={
                "mobile_number": "09125556666",
                "name": "Ali",
                "family": "Ahmadi",
                "password1": "Test@12345",
                "password2": "Test@12345",
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/register.html"
        )

        messages = list(
            get_messages(response.wsgi_request)
        )

        self.assertTrue(
            any(
                "خطایی در ثبت‌نام رخ داد" in str(message)
                for message in messages
            )
        )


class LogoutUserViewTests(BaseAccountTest):

    def setUp(self):
        super().setUp()
        self.activate_user()

    def test_logout_success(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:logout")
        )

        self.assertRedirects(
            response,
            reverse("main:index")
        )

        self.assertFalse(
            response.wsgi_request.user.is_authenticated
        )

    def test_shop_cart_is_cleared_after_logout(self):
        self.client.force_login(self.user)

        session = self.client.session
        session["shop_cart"] = {
            "1": {
                "qty": 2
            }
        }
        session.save()

        self.client.post(
            reverse("accounts:logout")
        )

        self.assertNotIn(
            "shop_cart",
            self.client.session
        )

    def test_logout_without_shop_cart(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:logout")
        )

        self.assertRedirects(
            response,
            reverse("main:index")
        )

        self.assertNotIn(
            "shop_cart",
            self.client.session
        )

    def test_anonymous_user_redirect_to_login(self):
        response = self.client.post(
            reverse("accounts:logout")
        )

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:logout')}"
        )


class LoginUserViewTests(BaseAccountTest):

    def setUp(self):
        super().setUp()
        self.activate_user()

    def test_get_login_page(self):
        response = self.client.get(
            reverse("accounts:login")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/login.html"
        )

    def test_get_uses_login_form(self):
        response = self.client.get(
            reverse("accounts:login")
        )

        self.assertIn(
            "form",
            response.context
        )

        self.assertIsInstance(
            response.context["form"],
            LoginUserForm
        )

    def test_post_valid_login(self):
        response = self.client.post(
            reverse("accounts:login"),
            data={
                "mobile_number": self.user.mobile_number,
                "password": "123456",
            }
        )

        self.assertTrue(
            response.wsgi_request.user.is_authenticated
        )

        self.assertRedirects(
            response,
            reverse("main:index")
        )

    def test_post_valid_login_with_next_url(self):
        next_url = reverse("main:index")

        response = self.client.post(
            f"{reverse('accounts:login')}?next={next_url}",
            data={
                "mobile_number": self.user.mobile_number,
                "password": "123456",
            }
        )

        self.assertRedirects(
            response,
            next_url
        )

    def test_post_invalid_password(self):
        response = self.client.post(
            reverse("accounts:login"),
            data={
                "mobile_number": self.user.mobile_number,
                "password": "WrongPassword",
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/login.html"
        )

        self.assertFalse(
            response.wsgi_request.user.is_authenticated
        )

    def test_post_invalid_form(self):
        response = self.client.post(
            reverse("accounts:login"),
            data={
                "mobile_number": "0912",
                "password": "",
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/login.html"
        )

        self.assertFalse(
            response.context["form"].is_valid()
        )

    def test_admin_cannot_login_from_user_panel(self):
        self.user.is_admin = True
        self.user.save()

        response = self.client.post(
            reverse("accounts:login"),
            data={
                "mobile_number": self.user.mobile_number,
                "password": "123456",
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/login.html"
        )

        self.assertFalse(
            response.wsgi_request.user.is_authenticated
        )


class ChangePasswordViewTests(BaseAccountTest):

    def test_get_change_password_page(self):
        response = self.client.get(
            reverse("accounts:change_password")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/change_password.html"
        )

    def test_get_uses_change_password_form(self):
        response = self.client.get(
            reverse("accounts:change_password")
        )

        self.assertIn(
            "form",
            response.context
        )

        self.assertIsInstance(
            response.context["form"],
            ChangePasswordForm
        )

    def test_post_change_password_requires_verified_code(self):
        self.set_user_session(
            mobile_number=self.user.mobile_number,
            remember_password=True,
            verified=False,
        )

        response = self.client.post(
            reverse("accounts:change_password"),
            data={
                "password1": "Test@12345",
                "password2": "Test@12345",
            }
        )

        self.assertEqual(
            response.json()["status"],
            "error"
        )

        self.user.refresh_from_db()

        self.assertFalse(
            self.user.check_password("Test@12345")
        )

    @patch("apps.accounts.views.utils.create_random_code")
    def test_post_valid_change_password(
        self,
        mock_create_random_code,
    ):
        mock_create_random_code.return_value = "12345"

        self.set_user_session(
            mobile_number=self.user.mobile_number
        )

        response = self.client.post(
            reverse("accounts:change_password"),
            data={
                "password1": "Test@12345",
                "password2": "Test@12345",
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.json()["status"],
            "success"
        )

        self.assertEqual(
            response.json()["redirect_url"],
            "/accounts/login/"
        )

    @patch("apps.accounts.views.utils.create_random_code")
    def test_post_password_changed(
        self,
        mock_create_random_code,
    ):
        mock_create_random_code.return_value = "12345"

        self.set_user_session(
            mobile_number=self.user.mobile_number
        )

        self.client.post(
            reverse("accounts:change_password"),
            data={
                "password1": "Test@12345",
                "password2": "Test@12345",
            }
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password("Test@12345")
        )

    @patch("apps.accounts.views.utils.create_random_code")
    def test_post_active_code_changed(
        self,
        mock_create_random_code,
    ):
        mock_create_random_code.return_value = "54321"

        self.set_user_session(
            mobile_number=self.user.mobile_number
        )

        self.client.post(
            reverse("accounts:change_password"),
            data={
                "password1": "Test@12345",
                "password2": "Test@12345",
            }
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.active_code,
            "54321"
        )

    def test_post_without_user_session(self):
        response = self.client.post(
            reverse("accounts:change_password"),
            data={
                "password1": "Test@12345",
                "password2": "Test@12345",
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.json()["status"],
            "error"
        )

        self.assertEqual(
            response.json()["message"],
            "نشست شما منقضی شده است."
        )

    def test_post_user_not_found(self):
        self.set_user_session(
            mobile_number="09129999999"
        )

        response = self.client.post(
            reverse("accounts:change_password"),
            data={
                "password1": "Test@12345",
                "password2": "Test@12345",
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.json()["status"],
            "error"
        )

        self.assertEqual(
            response.json()["message"],
            "کاربر پیدا نشد."
        )

    def test_post_invalid_form(self):
        response = self.client.post(
            reverse("accounts:change_password"),
            data={
                "password1": "123",
                "password2": "1234",
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.json()["status"],
            "error"
        )

        self.assertIn(
            "password2",
            response.json()["errors"]
        )


class VerifyRegisterCodeViewTests(BaseAccountTest):

    def test_get_verify_register_page(self):
        response = self.client.get(
            reverse("accounts:verify")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/verify_register_code.html"
        )

    def test_get_uses_verify_register_form(self):
        response = self.client.get(
            reverse("accounts:verify")
        )

        self.assertIn(
            "form",
            response.context
        )

        self.assertIsInstance(
            response.context["form"],
            VerifyRegisterForm
        )

    def test_post_without_user_session(self):
        response = self.client.post(
            reverse("accounts:verify"),
            data={
                "active_code": "12345"
            }
        )

        self.assertRedirects(
            response,
            reverse("accounts:register")
        )

    @patch("apps.accounts.views.utils.create_random_code")
    def test_post_correct_code_register_user(
        self,
        mock_create_random_code,
    ):
        mock_create_random_code.return_value = "99999"

        self.user.is_active = False
        self.user.save()

        self.set_user_session(
            mobile_number=self.user.mobile_number,
            active_code="12345",
        )

        response = self.client.post(
            reverse("accounts:verify"),
            data={
                "active_code": "12345"
            }
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.is_active
        )

        self.assertEqual(
            self.user.active_code,
            "99999"
        )

        self.assertRedirects(
            response,
            reverse("accounts:login")
        )

    def test_post_correct_code_change_password(self):
        self.set_user_session(
            mobile_number=self.user.mobile_number,
            active_code="12345",
            remember_password=True,
        )

        response = self.client.post(
            reverse("accounts:verify"),
            data={
                "active_code": "12345"
            }
        )

        self.assertRedirects(
            response,
            reverse("accounts:change_password")
        )

    def test_post_wrong_active_code(self):
        self.user.is_active = False
        self.user.save()

        self.set_user_session(
            mobile_number=self.user.mobile_number,
            active_code="12345",
        )

        response = self.client.post(
            reverse("accounts:verify"),
            data={
                "active_code": "99999"
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/verify_register_code.html"
        )

        self.user.refresh_from_db()

        self.assertFalse(
            self.user.is_active
        )

    def test_post_invalid_form(self):
        response = self.client.post(
            reverse("accounts:verify"),
            data={
                "active_code": ""
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/verify_register_code.html"
        )

        self.assertFalse(
            response.context["form"].is_valid()
        )

        self.assertIn(
            "active_code",
            response.context["form"].errors
        )

    def test_post_user_not_found(self):
        self.set_user_session(
            mobile_number="09129999999",
            active_code="12345",
        )

        response = self.client.post(
            reverse("accounts:verify"),
            data={
                "active_code": "12345"
            }
        )

        self.assertRedirects(
            response,
            reverse("accounts:register")
        )


class RememberPasswordViewTests(BaseAccountTest):

    def test_get_remember_password_page(self):
        response = self.client.get(
            reverse("accounts:remember_password")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/remember_password.html"
        )

    def test_get_uses_remember_password_form(self):
        response = self.client.get(
            reverse("accounts:remember_password")
        )

        self.assertIn(
            "form",
            response.context
        )

        self.assertIsInstance(
            response.context["form"],
            RememberPasswordForm
        )

    @patch("apps.accounts.views.utils.send_sms")
    @patch("apps.accounts.views.utils.create_random_code")
    def test_post_valid_mobile(
        self,
        mock_create_random_code,
        mock_send_sms,
    ):
        mock_create_random_code.return_value = "12345"

        response = self.client.post(
            reverse("accounts:remember_password"),
            data={
                "mobile_number": self.user.mobile_number,
            }
        )

        self.assertRedirects(
            response,
            reverse("accounts:verify")
        )

    @patch("apps.accounts.views.utils.send_sms")
    @patch("apps.accounts.views.utils.create_random_code")
    def test_post_send_sms(
        self,
        mock_create_random_code,
        mock_send_sms,
    ):
        mock_create_random_code.return_value = "12345"

        self.client.post(
            reverse("accounts:remember_password"),
            data={
                "mobile_number": self.user.mobile_number,
            }
        )

        mock_send_sms.assert_called_once_with(
            self.user.mobile_number,
            "12345"
        )

    @patch("apps.accounts.views.utils.send_sms")
    @patch("apps.accounts.views.utils.create_random_code")
    def test_post_active_code_changed(
        self,
        mock_create_random_code,
        mock_send_sms,
    ):
        mock_create_random_code.return_value = "54321"

        self.client.post(
            reverse("accounts:remember_password"),
            data={
                "mobile_number": self.user.mobile_number,
            }
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.active_code,
            "54321"
        )

    @patch("apps.accounts.views.utils.send_sms")
    @patch("apps.accounts.views.utils.create_random_code")
    def test_post_create_user_session(
        self,
        mock_create_random_code,
        mock_send_sms,
    ):
        mock_create_random_code.return_value = "12345"

        self.client.post(
            reverse("accounts:remember_password"),
            data={
                "mobile_number": self.user.mobile_number,
            }
        )

        session = self.client.session

        self.assertIn(
            "user_session",
            session
        )

        self.assertEqual(
            session["user_session"]["mobile_number"],
            self.user.mobile_number
        )

        self.assertEqual(
            session["user_session"]["active_code"],
            "12345"
        )

        self.assertTrue(
            session["user_session"]["remember_password"]
        )

    def test_post_user_not_found(self):
        response = self.client.post(
            reverse("accounts:remember_password"),
            data={
                "mobile_number": "09129999999",
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/remember_password.html"
        )

        self.assertFalse(
            response.context["form"].is_valid()
        )

    def test_post_invalid_form(self):
        response = self.client.post(
            reverse("accounts:remember_password"),
            data={
                "mobile_number": "0912",
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/remember_password.html"
        )

        self.assertFalse(
            response.context["form"].is_valid()
        )

        self.assertIn(
            "mobile_number",
            response.context["form"].errors
        )


class UserPanelViewTests(BaseAccountTest):

    def setUp(self):
        super().setUp()
        self.activate_user()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse("accounts:userpanel")
        )

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:userpanel')}"
        )

    def test_get_user_panel_page(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("accounts:userpanel")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/userpanel.html"
        )

    def test_context_contains_user_and_profile(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("accounts:userpanel")
        )

        self.assertEqual(
            response.context["user"],
            self.user
        )

        self.assertEqual(
            response.context["profile"],
            self.profile
        )


class SellerDashboardViewTests(BaseAccountTest):

    def setUp(self):
        super().setUp()
        self.activate_user()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse("accounts:seller_dashboard")
        )

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:seller_dashboard')}"
        )

    def test_redirect_if_store_not_exists(self):
        self.client.force_login(self.user)

        Store.objects.filter(
            user=self.user
        ).delete()

        response = self.client.get(
            reverse("accounts:seller_dashboard")
        )

        self.assertRedirects(
            response,
            reverse("accounts:create_store")
        )

    def test_get_seller_dashboard_page(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("accounts:seller_dashboard")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/seller_dashboard.html"
        )

    def test_context_contains_user_profile_store(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("accounts:seller_dashboard")
        )

        self.assertEqual(
            response.context["user"],
            self.user
        )

        self.assertEqual(
            response.context["profile"],
            self.profile
        )

        self.assertEqual(
            response.context["store"],
            self.store
        )


class UpdateProfileViewTests(BaseAccountTest):

    def setUp(self):
        super().setUp()
        self.activate_user()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse("accounts:update_profile")
        )

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:update_profile')}"
        )

    def test_get_update_profile_page(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("accounts:update_profile")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/update_profile.html"
        )

    def test_get_create_profile_if_not_exists(self):
        self.client.force_login(self.user)

        UserProfile.objects.filter(
            user=self.user
        ).delete()

        self.assertFalse(
            UserProfile.objects.filter(
                user=self.user
            ).exists()
        )

        self.client.get(
            reverse("accounts:update_profile")
        )

        self.assertTrue(
            UserProfile.objects.filter(
                user=self.user
            ).exists()
        )

    def test_get_context_contains_forms(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("accounts:update_profile")
        )

        self.assertIn(
            "user_form",
            response.context
        )

        self.assertIn(
            "profile_form",
            response.context
        )

        self.assertIsInstance(
            response.context["user_form"],
            UpdateProfileForm
        )

        self.assertIsInstance(
            response.context["profile_form"],
            UpdateUserProfileForm
        )

    def test_post_valid_forms(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:update_profile"),
            data={
                "name": "علی",
                "family": "محمدی",
                "email": "ali@test.com",
                "address": "تهران",
            },
            files={
                "image_name": self.image,
            }
        )

        self.assertRedirects(
            response,
            reverse("accounts:userpanel")
        )

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(
            self.user.name,
            "علی"
        )

        self.assertEqual(
            self.user.family,
            "محمدی"
        )

        self.assertEqual(
            self.user.email,
            "ali@test.com"
        )

        self.assertEqual(
            self.profile.address,
            "تهران"
        )

    def test_post_invalid_forms(self):
        self.client.force_login(self.user)

        old_name = self.user.name
        old_address = self.profile.address

        response = self.client.post(
            reverse("accounts:update_profile"),
            data={
                "name": self.user.name,
                "family": self.user.family,
                "email": "invalid-email",
                "address": "آدرس جدید",
            }
        )

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/update_profile.html"
        )

        self.assertFalse(
            response.context["user_form"].is_valid()
        )

        self.assertEqual(
            self.user.name,
            old_name
        )

        self.assertEqual(
            self.profile.address,
            old_address
        )


class CreateStoreViewTests(BaseAccountTest):

    def setUp(self):
        super().setUp()
        self.activate_user()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse("accounts:create_store")
        )

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:create_store')}"
        )

    def test_get_create_store_page(self):
        self.client.force_login(self.user)

        Store.objects.filter(
            user=self.user
        ).delete()

        response = self.client.get(
            reverse("accounts:create_store")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/create_store.html"
        )

        self.assertIsInstance(
            response.context["form"],
            CreateStoreForm
        )

    def test_get_redirect_if_store_exists(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("accounts:create_store")
        )

        self.assertRedirects(
            response,
            reverse("accounts:edit_store")
        )

    def test_post_valid_form(self):
        self.client.force_login(self.user)

        Store.objects.filter(
            user=self.user
        ).delete()

        response = self.client.post(
            reverse("accounts:create_store"),
            data={
                "store_name": "فروشگاه تست",
                "store_phone": "02112345671",
                "address": "تهران",
                "description": "توضیحات تست",
            }
        )

        self.assertRedirects(
            response,
            reverse("accounts:seller_dashboard")
        )

        store = Store.objects.get(
            user=self.user
        )

        self.assertEqual(
            store.store_name,
            "فروشگاه تست"
        )

        self.assertEqual(
            store.store_phone,
            "02112345671"
        )

    def test_post_if_store_exists(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:create_store"),
            data={
                "store_name": "فروشگاه جدید",
                "store_phone": "02199999999",
                "address": "آدرس جدید",
                "description": "توضیحات جدید",
            }
        )

        self.assertRedirects(
            response,
            reverse("accounts:edit_store")
        )

        self.assertEqual(
            Store.objects.filter(
                user=self.user
            ).count(),
            1
        )

    def test_post_invalid_form(self):
        self.client.force_login(self.user)

        Store.objects.filter(
            user=self.user
        ).delete()

        response = self.client.post(
            reverse("accounts:create_store"),
            data={
                "store_name": "",
                "store_phone": "123",
                "address": "",
                "description": "",
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/create_store.html"
        )

        self.assertFalse(
            response.context["form"].is_valid()
        )

        self.assertEqual(
            Store.objects.filter(
                user=self.user
            ).count(),
            0
        )


class EditStoreViewTests(BaseAccountTest):

    def setUp(self):
        super().setUp()
        self.activate_user()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse("accounts:edit_store")
        )

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:edit_store')}"
        )

    def test_get_edit_store_page(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("accounts:edit_store")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/edit_store.html"
        )

        self.assertIsInstance(
            response.context["form"],
            EditStoreForm
        )

    def test_get_redirects_to_create_store_if_store_not_exists(self):
        self.client.force_login(self.user)

        Store.objects.filter(
            user=self.user
        ).delete()

        response = self.client.get(
            reverse("accounts:edit_store")
        )

        self.assertRedirects(
            response,
            reverse("accounts:create_store")
        )

    def test_post_valid_form(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:edit_store"),
            data={
                "store_name": "فروشگاه جدید",
                "store_phone": "02112345673",
                "address": "آدرس جدید",
                "description": "توضیحات جدید",
            },
            files={
                "logo": self.image,
            }
        )

        self.assertRedirects(
            response,
            reverse("accounts:seller_dashboard")
        )

        self.store.refresh_from_db()

        self.assertEqual(
            self.store.store_name,
            "فروشگاه جدید"
        )

        self.assertEqual(
            self.store.store_phone,
            "02112345673"
        )

        self.assertEqual(
            self.store.address,
            "آدرس جدید"
        )

        self.assertEqual(
            self.store.description,
            "توضیحات جدید"
        )

    def test_post_valid_form_without_logo(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:edit_store"),
            data={
                "store_name": "فروشگاه جدید",
                "store_phone": "02112345675",
                "address": "آدرس جدید",
                "description": "توضیحات جدید",
            }
        )

        self.assertRedirects(
            response,
            reverse("accounts:seller_dashboard")
        )

    def test_post_invalid_form(self):
        self.client.force_login(self.user)

        old_name = self.store.store_name
        old_phone = self.store.store_phone
        old_address = self.store.address
        old_description = self.store.description

        response = self.client.post(
            reverse("accounts:edit_store"),
            data={
                "store_name": "",
                "store_phone": "123",
                "address": "",
                "description": "",
            }
        )

        self.store.refresh_from_db()

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/edit_store.html"
        )

        self.assertFalse(
            response.context["form"].is_valid()
        )

        self.assertEqual(
            self.store.store_name,
            old_name
        )

        self.assertEqual(
            self.store.store_phone,
            old_phone
        )

        self.assertEqual(
            self.store.address,
            old_address
        )

        self.assertEqual(
            self.store.description,
            old_description
        )


class StoreDetailViewTests(BaseAccountTest):

    def setUp(self):
        super().setUp()
        self.activate_user()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse("accounts:store_detail")
        )

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:store_detail')}"
        )

    def test_get_store_detail_page(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("accounts:store_detail")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/store_detail.html"
        )

    def test_get_redirects_to_create_store_if_store_not_exists(self):
        self.client.force_login(self.user)

        Store.objects.filter(
            user=self.user
        ).delete()

        response = self.client.get(
            reverse("accounts:store_detail")
        )

        self.assertRedirects(
            response,
            reverse("accounts:create_store")
        )

    def test_context_contains_store(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("accounts:store_detail")
        )

        self.assertEqual(
            response.context["store"],
            self.store
        )


class ShowLastOrdersTests(BaseAccountTest):

    def setUp(self):
        super().setUp()
        self.activate_user()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse("accounts:show_last_orders")
        )

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:show_last_orders')}"
        )

    def test_show_last_orders(self):
        self.client.force_login(self.user)

        for _ in range(5):
            Order.objects.create(
                customer=self.profile,
                store=self.store,
                is_finally=True
            )

        response = self.client.get(
            reverse("accounts:show_last_orders")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/partials/show_last_orders.html"
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/show_last_orders.html"
        )

        self.assertEqual(
            len(response.context["orders"]),
            4
        )


class ShowUserPaymentsTests(BaseAccountTest):

    def setUp(self):
        super().setUp()
        self.activate_user()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse("accounts:show_user_payments")
        )

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:show_user_payments')}"
        )

    def test_show_user_payments(self):
        self.client.force_login(self.user)

        order = Order.objects.create(
            customer=self.profile,
            store=self.store,
            is_finally=True
        )

        Payment.objects.create(
            customer=self.profile,
            order=order,
            amount=1000
        )

        response = self.client.get(
            reverse("accounts:show_user_payments")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "accounts_app/show_user_payments.html"
        )

        self.assertEqual(
            response.context["payments"].count(),
            1
        )