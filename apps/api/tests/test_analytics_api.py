from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import (
    CustomUser,
    Store,
)


class AnalyticsAPITests(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            mobile_number="09120000000",
            password="123456",
            name="Ali",
            family="Ahmadi",
        )

        self.store = Store.objects.create(
            user=self.user,
            store_name="Digital Shop",
            store_phone="09121111111",
            is_active=True,
        )

        self.other_user = CustomUser.objects.create_user(
            mobile_number="09123333333",
            password="123456",
            name="Reza",
            family="Ahmadi",
        )

        self.other_store = Store.objects.create(
            user=self.other_user,
            store_name="Other Shop",
            store_phone="09124444444",
            is_active=True,
        )

        self.url = reverse(
            "api:dashboard",
            kwargs={
                "store_id": self.store.id,
            },
        )

    def test_unauthenticated_user_cannot_access(self):
        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_store_owner_can_access(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_user_without_store_cannot_access(self):
        user_without_store = CustomUser.objects.create_user(
            mobile_number="09125555555",
            password="123456",
            name="Test",
            family="User",
        )

        self.client.force_authenticate(
            user=user_without_store
        )

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_inactive_store_owner_cannot_access(self):
        self.store.is_active = False
        self.store.save()

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_other_store_owner_cannot_access(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )