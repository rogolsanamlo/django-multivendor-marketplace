from django.db import IntegrityError
from apps.accounts.models import CustomUser, Store, UserProfile
from apps.tests.base import BaseAccountTest


class CustomUserTests(BaseAccountTest):

    def test_create_user_success(self):
        user = CustomUser.objects.create_user(
            mobile_number="09120000111",
            password="123456",
            name="Ali",
            family="Ahmadi",
            email="ali@test.com",
        )

        self.assertEqual(user.mobile_number, "09120000111")
        self.assertEqual(user.name, "Ali")
        self.assertEqual(user.family, "Ahmadi")
        self.assertEqual(user.email, "ali@test.com")
        self.assertTrue(user.check_password("123456"))
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_active)

    def test_create_user_without_mobile_number(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                mobile_number="",
                password="123456",
            )

    def test_create_superuser(self):
        user = CustomUser.objects.create_superuser(
            mobile_number="09123334444",
            email="admin@test.com",
            name="Ali",
            family="Ahmadi",
            password="123456",
        )

        self.assertEqual(user.mobile_number, "09123334444")
        self.assertTrue(user.check_password("123456"))
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_default_is_active(self):
        user = CustomUser.objects.create_user(
            mobile_number="09120000002",
            password="123456",
        )

        self.assertFalse(user.is_active)

    def test_default_is_admin(self):
        user = CustomUser.objects.create_user(
            mobile_number="09120000003",
            password="123456",
        )

        self.assertFalse(user.is_admin)

    def test_default_is_superuser(self):
        user = CustomUser.objects.create_user(
            mobile_number="09120000004",
            password="123456",
        )

        self.assertFalse(user.is_superuser)

    def test_user_str(self):
        self.assertEqual(str(self.user), "Ali Ahmadi")

    def test_is_staff_property_false(self):
        user = CustomUser.objects.create_user(
            mobile_number="09120000006",
            password="123456",
        )

        self.assertFalse(user.is_staff)

    def test_is_staff_property_true_for_admin(self):
        user = CustomUser.objects.create_superuser(
            mobile_number="09120000008",
            email="admin2@test.com",
            name="Sara",
            family="Karimi",
            password="123456",
        )

        self.assertTrue(user.is_staff)

    def test_email_is_normalized(self):
        user = CustomUser.objects.create_user(
            mobile_number="09120000009",
            password="123456",
            email="Ali@TEST.com",
        )

        self.assertEqual(user.email, "Ali@test.com")


class UserProfileTests(BaseAccountTest):

    def test_user_profile_created_after_user_creation(self):
        user = CustomUser.objects.create_user(
            mobile_number="09123334444",
            password="123456",
        )

        self.assertTrue(
            UserProfile.objects.filter(user=user).exists()
        )

    def test_profile_is_created_only_once(self):
        count_before = UserProfile.objects.filter(
            user=self.user
        ).count()

        self.user.name = "New Name"
        self.user.save()

        count_after = UserProfile.objects.filter(
            user=self.user
        ).count()

        self.assertEqual(count_before, count_after)

    def test_address(self):
        self.profile.address = "Tehran"
        self.profile.save()
        self.profile.refresh_from_db()

        self.assertEqual(self.profile.address, "Tehran")

    def test_user_profile_relation(self):
        self.assertEqual(self.user.userprofile, self.profile)

    def test_delete_user_delete_profile(self):
        profile_id = self.profile.pk

        self.user.delete()

        self.assertFalse(
            UserProfile.objects.filter(pk=profile_id).exists()
        )

    def test_user_profile_str(self):
        self.assertEqual(str(self.profile), str(self.user))

    def test_profile_image(self):
        self.profile.image_name = self.image
        self.profile.save()

        self.assertTrue(
            self.profile.image_name.name.endswith(".jpg")
        )

    def test_profile_image_is_optional(self):
        self.assertFalse(bool(self.profile.image_name))


class StoreTests(BaseAccountTest):

    def test_store_relation(self):
        self.assertEqual(self.user.store, self.store)

    def test_store_address(self):
        self.store.address = "Tehran"
        self.store.save()
        self.store.refresh_from_db()

        self.assertEqual(self.store.address, "Tehran")

    def test_store_default_is_active(self):
        self.assertFalse(self.store.is_active)

    def test_store_str(self):
        self.assertEqual(str(self.store), "Digital Shop")

    def test_slug_created(self):
        self.assertEqual(self.store.slug, "digital-shop")

    def test_unique_slug(self):
        user2 = CustomUser.objects.create_user(
            mobile_number="09129999999",
            password="123456",
        )

        store2 = Store.objects.create(
            user=user2,
            store_name="Digital Shop",
            store_phone="09128888888",
        )

        self.assertEqual(store2.slug, "digital-shop-1")

    def test_slug_is_not_overwritten(self):
        self.store.slug = "custom-slug"
        self.store.save()
        self.store.refresh_from_db()

        self.assertEqual(self.store.slug, "custom-slug")

    def test_delete_user_delete_store(self):
        store_id = self.store.pk

        self.user.delete()

        self.assertFalse(
            Store.objects.filter(pk=store_id).exists()
        )

    def test_store_logo(self):
        self.store.logo = self.image
        self.store.save()

        self.assertTrue(
            self.store.logo.name.endswith(".jpg")
        )

    def test_store_logo_is_optional(self):
        self.assertFalse(bool(self.store.logo))

    def test_store_description_default(self):
        self.assertEqual(self.store.description, "")

    def test_store_is_unique_phone(self):
        user2 = CustomUser.objects.create_user(
            mobile_number="09127777777",
            password="123456",
        )

        with self.assertRaises(IntegrityError):
            Store.objects.create(
                user=user2,
                store_name="Another Shop",
                store_phone="09121111111",
            )

    def test_store_slug_fallback_for_invalid_name(self):
        user3 = CustomUser.objects.create_user(
            mobile_number="09126666666",
            password="123456",
        )

        store3 = Store.objects.create(
            user=user3,
            store_name="!!!",
            store_phone="09125555555",
        )

        self.assertEqual(store3.slug, "store")