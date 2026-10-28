from django.test import TestCase

from apps.accounts.models import CustomUser, UserProfile


class CreateUserProfileSignalTests(TestCase):

    def test_profile_created_when_user_created(self):
        user = CustomUser.objects.create_user(
            mobile_number="09123456789",
            password="Test@123"
        )

        self.assertTrue(
            UserProfile.objects.filter(
                user=user
            ).exists()
        )

    def test_profile_not_created_twice(self):
        user = CustomUser.objects.create_user(
            mobile_number="09123456789",
            password="Test@123"
        )

        user.name = "Ali"
        user.save()

        self.assertEqual(
            UserProfile.objects.filter(
                user=user
            ).count(),
            1
        )