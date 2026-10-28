import shutil
import tempfile
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import Store
from apps.products.models import Brand, Product, ProductGroup, StoreProduct
from apps.warehouses.models import Warehouse


class SeedDemoTests(TestCase):

    def setUp(self):
        # Generated pictures go to a throw-away folder, not to the real media.
        media_root = tempfile.mkdtemp()

        self.addCleanup(shutil.rmtree, media_root, ignore_errors=True)

        override = override_settings(MEDIA_ROOT=media_root)
        override.enable()
        self.addCleanup(override.disable)

    def seed(self):
        call_command("seed_demo", "--force", stdout=StringIO())

    def counts(self):
        return (
            ProductGroup.objects.count(),
            Brand.objects.count(),
            Product.objects.count(),
            Store.objects.count(),
            StoreProduct.objects.count(),
            Warehouse.objects.count(),
        )

    def test_creates_a_complete_catalog(self):
        self.seed()

        self.assertEqual(
            ProductGroup.objects.filter(group_parent__isnull=True).count(),
            3,
        )

        self.assertEqual(
            ProductGroup.objects.filter(group_parent__isnull=False).count(),
            6,
        )

        self.assertEqual(Product.objects.count(), 12)
        self.assertEqual(Store.objects.filter(is_active=True).count(), 2)
        self.assertEqual(StoreProduct.objects.count(), 18)

        for store_product in StoreProduct.objects.all():
            self.assertGreater(store_product.get_number_in_warehouse(), 0)

    def test_two_stores_sell_the_same_product_at_different_prices(self):
        self.seed()

        prices = set(
            StoreProduct.objects
            .filter(product__slug="demo-phone-alpha")
            .values_list("price", flat=True)
        )

        self.assertEqual(len(prices), 2)

    def test_running_twice_does_not_duplicate_anything(self):
        self.seed()
        first = self.counts()

        self.seed()

        self.assertEqual(self.counts(), first)

    def test_refuses_to_run_without_force_when_debug_is_off(self):
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())

        self.assertEqual(Product.objects.count(), 0)

    def test_demo_products_appear_on_the_site(self):
        self.seed()

        group = ProductGroup.objects.get(group_title="لبنیات")

        response = self.client.get(
            reverse(
                "products:products_by_group",
                kwargs={"slug": group.slug},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "کره پاستوریزه")

        self.assertEqual(
            self.client.get(reverse("main:index")).status_code,
            200,
        )
