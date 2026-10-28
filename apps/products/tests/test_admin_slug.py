from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from apps.accounts.models import CustomUser
from apps.products.models import Brand
from utils import generate_unique_slug


def make_image():
    image_io = BytesIO()

    Image.new("RGB", (50, 50), "white").save(image_io, format="JPEG")

    return SimpleUploadedFile(
        "brand.jpg",
        image_io.getvalue(),
        content_type="image/jpeg",
    )


class GenerateUniqueSlugTests(TestCase):

    def test_latin_title_becomes_slug(self):
        self.assertEqual(
            generate_unique_slug(Brand, "Samsung Galaxy", "brand"),
            "samsung-galaxy",
        )

    def test_existing_slug_gets_a_counter(self):
        Brand.objects.create(brand_title="Samsung", slug="samsung")

        self.assertEqual(
            generate_unique_slug(Brand, "Samsung", "brand"),
            "samsung-2",
        )

    def test_persian_title_uses_fallback_prefix(self):
        slug = generate_unique_slug(Brand, "سامسونگ", "brand")

        self.assertTrue(slug.startswith("brand-"))
        self.assertGreater(len(slug), len("brand-"))


class BrandAdminSlugTests(TestCase):

    def setUp(self):
        self.admin_user = CustomUser.objects.create_superuser(
            mobile_number="09121112244",
            password="1234",
            email="slug-admin@test.com",
            name="Admin",
            family="Test",
        )

        self.client.force_login(self.admin_user)

    def test_add_form_explains_optional_slug(self):
        response = self.client.get(reverse("admin:products_brand_add"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "اختیاری؛ اگر خالی بماند")

    def test_blank_slug_is_generated(self):
        response = self.client.post(
            reverse("admin:products_brand_add"),
            data={
                "brand_title": "سامسونگ",
                "slug": "",
                "image_name": make_image(),
            },
        )

        self.assertEqual(response.status_code, 302)

        brand = Brand.objects.get()

        self.assertTrue(brand.slug.startswith("brand-"))

    def test_latin_title_gives_readable_slug(self):
        self.client.post(
            reverse("admin:products_brand_add"),
            data={
                "brand_title": "Samsung",
                "slug": "",
                "image_name": make_image(),
            },
        )

        self.assertEqual(Brand.objects.get().slug, "samsung")
