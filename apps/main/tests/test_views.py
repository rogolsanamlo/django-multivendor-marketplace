from django.test import TestCase
from django.urls import reverse


class MainViewTest(TestCase):

    def test_index_view_returns_200(self):

        response = self.client.get(
            reverse("main:index")
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_index_view_uses_correct_template(self):

        response = self.client.get(
            reverse("main:index")
        )

        self.assertTemplateUsed(
            response,
            "main_app/index.html"
        )



class StaticPagesTest(TestCase):

    def test_about_us_page(self):
        response = self.client.get(reverse("main:about_us"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main_app/about_us.html")

    def test_contact_us_page(self):
        response = self.client.get(reverse("main:contact_us"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main_app/contact_us.html")
