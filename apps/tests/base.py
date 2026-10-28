from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from apps.accounts.models import CustomUser, Store


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

        self.image = self.create_test_image()

        self.store = Store.objects.create(
            user=self.user,
            store_name="Digital Shop",
            store_phone="09121111111",
        )

    def create_test_image(self):
        image = Image.new(
            "RGB",
            (100, 100),
            "white",
        )

        image_io = BytesIO()

        image.save(
            image_io,
            format="JPEG",
        )

        image_io.seek(0)

        return SimpleUploadedFile(
            "test.jpg",
            image_io.read(),
            content_type="image/jpeg",
        )

    def activate_user(self):
        self.user.is_active = True
        self.user.save()

    def set_user_session(
        self,
        mobile_number=None,
        active_code=None,
        remember_password=False,
        verified=True,
    ):
        session = self.client.session

        session["user_session"] = {
            "mobile_number": mobile_number or self.user.mobile_number,
            "active_code": active_code,
            "remember_password": remember_password,
            "verified": verified,
        }

        session.save()