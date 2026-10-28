from django.urls import reverse

from rest_framework.test import APITestCase

from apps.accounts.models import (
    CustomUser,
    Store,
    UserProfile,
)


class AccountsAPITest(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            mobile_number="09121111111",
            email="user@example.com",
            name="Test",
            family="User",
            password="Test123!",
        )

        self.other_user = CustomUser.objects.create_user(
            mobile_number="09122222222",
            email="other@example.com",
            name="Other",
            family="User",
            password="Test123!",
        )

        self.profile, _ = UserProfile.objects.get_or_create(
            user=self.user
        )

        self.store = Store.objects.create(
            user=self.user,
            store_name="Test Store",
            store_phone="09123333333",
            slug="test-store",
            is_active=True,
        )

        self.profile_url = reverse(
            "api:profile"
        )

        self.profile_update_url = reverse(
            "api:profile-update"
        )

        self.store_url = reverse(
            "api:my-store"
        )

        self.store_create_url = reverse(
            "api:store-create"
        )

        self.store_update_url = reverse(
            "api:store-update"
        )

    def test_unauthenticated_cannot_access_profile(self):
        response = self.client.get(
            self.profile_url
        )

        self.assertIn(
            response.status_code,
            [401, 403],
        )

    def test_unauthenticated_cannot_update_profile(self):
        response = self.client.patch(
            self.profile_update_url,
            {
                "name": "Hacker",
            },
        )

        self.assertIn(
            response.status_code,
            [401, 403],
        )

    def test_unauthenticated_cannot_access_store(self):
        response = self.client.get(
            self.store_url
        )

        self.assertIn(
            response.status_code,
            [401, 403],
        )

    def test_unauthenticated_cannot_create_store(self):
        response = self.client.post(
            self.store_create_url,
            {
                "store_name": "Fake Store",
                "store_phone": "09124444444",
                "address": "Test",
            },
        )

        self.assertIn(
            response.status_code,
            [401, 403],
        )

    def test_authenticated_user_can_read_own_profile(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.profile_url
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["user"]["id"],
            self.user.id,
        )

    def test_authenticated_user_can_update_own_profile(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            self.profile_update_url,
            {
                "name": "NewName",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.name,
            "NewName",
        )

    def test_user_cannot_change_mobile_number(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            self.profile_update_url,
            {
                "mobile_number": "09129999999",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.mobile_number,
            "09121111111",
        )

    def test_authenticated_user_can_read_own_store(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.store_url
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["id"],
            self.store.id,
        )

    def test_authenticated_user_can_update_own_store(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            self.store_update_url,
            {
                "store_name": "New Store Name",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.store.refresh_from_db()

        self.assertEqual(
            self.store.store_name,
            "New Store Name",
        )

    def test_user_cannot_create_second_store(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.store_create_url,
            {
                "store_name": "Second Store",
                "store_phone": "09126666666",
                "address": "Another Address",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            Store.objects.filter(
                user=self.user
            ).count(),
            1,
        )

    def test_authenticated_user_can_create_store(self):
        user_without_store = CustomUser.objects.create_user(
            mobile_number="09127777777",
            email="new@example.com",
            name="New",
            family="User",
            password="Test123!",
        )

        self.client.force_authenticate(
            user=user_without_store
        )

        response = self.client.post(
            self.store_create_url,
            {
                "store_name": "New Store",
                "store_phone": "09128888888",
                "address": "New Address",
                "description": "My store",
            },
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertTrue(
            Store.objects.filter(
                user=user_without_store
            ).exists()
        )

    def test_store_user_cannot_be_forged(self):
        user_without_store = CustomUser.objects.create_user(
            mobile_number="09129999999",
            email="third@example.com",
            name="Third",
            family="User",
            password="Test123!",
        )

        self.client.force_authenticate(
            user=user_without_store
        )

        response = self.client.post(
            self.store_create_url,
            {
                "user": self.user.id,
                "store_name": "My Store",
                "store_phone": "09123334444",
                "address": "Test",
            },
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        store = Store.objects.get(
            user=user_without_store
        )

        self.assertEqual(
            store.user,
            user_without_store,
        )