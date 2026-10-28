from django.contrib.admin.sites import site
from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.accounts.models import CustomUser, Store
from apps.products.admin import (
    BrandAdmin,
    FeatureAdmin,
    ProductAdmin,
    ProductGroupAdmin,
    export_json,
)
from apps.products.models import (
    Brand,
    Feature,
    FeatureValue,
    Product,
    ProductFeature,
    ProductGroup,
    StoreProduct,
)


class BaseAdminTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.user = CustomUser.objects.create_superuser(
            mobile_number="09121112233",
            password="1234",
            email="admin@test.com",
            name="Admin",
            family="Test",
        )

        self.client.force_login(self.user)

        self.store = Store.objects.create(
            user=self.user,
            store_name="Digital Store",
            store_phone="09121111111",
            is_active=True,
        )

        self.brand = Brand.objects.create(
            brand_title="Samsung",
            slug="samsung",
        )

        self.group = ProductGroup.objects.create(
            group_title="Mobile",
            slug="mobile",
            is_active=True,
        )

        self.product = Product.objects.create(
            product_name="Galaxy S25",
            brand=self.brand,
            slug="galaxy-s25",
            is_active=True,
        )

        self.product.product_group.add(
            self.group
        )

        self.store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=15000000,
            is_active=True,
        )

        self.feature = Feature.objects.create(
            feature_name="Color"
        )

        self.feature.product_group.add(
            self.group
        )

        self.feature_value = FeatureValue.objects.create(
            value_title="Black",
            feature=self.feature,
        )

        ProductFeature.objects.create(
            product=self.product,
            feature=self.feature,
            value="Black",
            filter_value=self.feature_value,
        )


# ==================================================
# BrandAdminTests
# ==================================================

class BrandAdminTests(BaseAdminTest):

    def test_changelist(self):

        response = self.client.get(
            reverse("admin:products_brand_changelist")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Samsung")

    def test_change_page(self):

        response = self.client.get(
            reverse(
                "admin:products_brand_change",
                args=[self.brand.pk]
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_search(self):

        response = self.client.get(
            reverse("admin:products_brand_changelist"),
            {"q": "Samsung"},
        )

        self.assertContains(response, "Samsung")

    def test_admin_configuration(self):

        admin_obj = BrandAdmin(
            Brand,
            site
        )

        self.assertEqual(
            admin_obj.search_fields,
            ("brand_title",)
        )

        self.assertEqual(
            admin_obj.ordering,
            ("brand_title",)
        )


# ==================================================
# ProductGroupAdminTests
# ==================================================

class ProductGroupAdminTests(BaseAdminTest):

    def setUp(self):

        super().setUp()

        self.child = ProductGroup.objects.create(
            group_title="Android",
            slug="android",
            group_parent=self.group,
            is_active=True,
        )

    def test_changelist(self):

        response = self.client.get(
            reverse("admin:products_productgroup_changelist")
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Mobile")

    def test_search(self):

        response = self.client.get(
            reverse("admin:products_productgroup_changelist"),
            {"q": "Mobile"},
        )

        self.assertContains(response, "Mobile")

    def test_filter(self):

        response = self.client.get(
            reverse("admin:products_productgroup_changelist"),
            {"group": self.group.id},
        )

        self.assertEqual(response.status_code, 200)

    def test_count_sub_group(self):

        admin_obj = ProductGroupAdmin(
            ProductGroup,
            site,
        )

        obj = admin_obj.get_queryset(
            self.factory.get("/")
        ).get(pk=self.group.pk)

        self.assertEqual(
            admin_obj.count_sub_group(obj),
            1,
        )

    def test_count_product(self):

        admin_obj = ProductGroupAdmin(
            ProductGroup,
            site,
        )

        obj = admin_obj.get_queryset(
            self.factory.get("/")
        ).get(pk=self.group.pk)

        self.assertEqual(
            admin_obj.count_product_of_group(obj),
            1,
        )

    def test_de_active_action(self):

        url = reverse("admin:products_productgroup_changelist")
        data = {
            "action": "de_active_product_group",
            "_selected_action": [self.group.pk],
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.group.refresh_from_db()
        self.assertFalse(self.group.is_active)

    def test_active_action(self):

        self.group.is_active = False
        self.group.save()
        url = reverse("admin:products_productgroup_changelist")
        data = {
            "action": "active_product_group",
            "_selected_action": [self.group.pk],
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.group.refresh_from_db()
        self.assertTrue(self.group.is_active)

    def test_export_json(self):

        request = self.factory.get("/")

        queryset = ProductGroup.objects.filter(
            pk=self.group.pk
        )

        response = export_json(
            None,
            request,
            queryset,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response["Content-Type"],
            "application/json",
        )


# ==================================================
# FeatureAdminTests
# ==================================================

class FeatureAdminTests(BaseAdminTest):

    def test_changelist(self):

        response = self.client.get(
            reverse("admin:products_feature_changelist")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Color",
        )

    def test_display_groups(self):

        admin_obj = FeatureAdmin(
            Feature,
            site,
        )

        value = admin_obj.display_groups(
            self.feature
        )

        self.assertEqual(
            value,
            "Mobile",
        )

    def test_display_feature_values(self):

        admin_obj = FeatureAdmin(
            Feature,
            site,
        )

        value = admin_obj.display_feature_values(
            self.feature
        )

        self.assertIn(
            "Black",
            value,
        )

    def test_search(self):

        response = self.client.get(
            reverse("admin:products_feature_changelist"),
            {"q": "Color"},
        )

        self.assertContains(
                response,
                "Color",
            )

    def test_formfield_queryset(self):

        admin_obj = FeatureAdmin(
            Feature,
            site,
        )

        request = self.factory.get("/")

        field = admin_obj.formfield_for_manytomany(
            Feature._meta.get_field("product_group"),
            request,
        )

        self.assertTrue(
            all(
                obj.group_parent is not None
                for obj in field.queryset
            )
        )

# ==================================================
# ProductAdminTests
# ==================================================

class ProductAdminTests(BaseAdminTest):

    def setUp(self):
        super().setUp()

        self.child_group = ProductGroup.objects.create(
            group_title="Android",
            slug="android",
            group_parent=self.group,
            is_active=True
        )

        self.product.product_group.clear()
        self.product.product_group.add(self.child_group)

    def test_product_changelist(self):
        response = self.client.get(
            reverse("admin:products_product_changelist")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Galaxy S25")

    def test_display_product_groups(self):
        ma = ProductAdmin(Product, site)

        self.assertEqual(
            ma.display_product_groups(self.product),
            "Android"
        )

    def test_product_deactivate_action(self):

        url = reverse("admin:products_product_changelist")
        data = {
            "action": "de_active_product",
            "_selected_action": [self.product.pk],
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertFalse(self.product.is_active)

    def test_product_activate_action(self):

        self.product.is_active = False
        self.product.save()
        url = reverse("admin:products_product_changelist")
        data = {
            "action": "active_product",
            "_selected_action": [self.product.pk],
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertTrue(self.product.is_active)

    def test_formfield_for_manytomany(self):
        ma = ProductAdmin(Product, site)

        field = ma.formfield_for_manytomany(
            Product._meta.get_field("product_group"),
            request=None
        )

        self.assertIn(
            self.child_group,
            field.queryset
        )

        self.assertNotIn(
            self.group,
            field.queryset
        )

    def test_product_change_page(self):
        response = self.client.get(
            reverse(
                "admin:products_product_change",
                args=[self.product.pk]
            )
        )

        self.assertEqual(response.status_code, 200)


# ==================================================
# StoreProductAdminTests
# ==================================================

class StoreProductAdminTests(BaseAdminTest):

    def setUp(self):
        super().setUp()

        self.another_user = CustomUser.objects.create_user(
            mobile_number="09120000001",
            password="pass",
            email="store@test.com",
            name="Store",
            family="Owner",
        )
        self.store = Store.objects.create(
            user=self.another_user,
            store_name="Digital Store",
            is_active=True
        )

        self.store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=10000000,
            is_active=True
        )

    def test_store_product_changelist(self):
        response = self.client.get(
            reverse("admin:products_storeproduct_changelist")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Digital Store")

    def test_store_product_deactivate_action(self):

        url = reverse("admin:products_storeproduct_changelist")
        data = {
            "action": "de_active_product",
            "_selected_action": [self.store_product.pk],
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.store_product.refresh_from_db()
        self.assertFalse(self.store_product.is_active)

    def test_store_product_activate_action(self):

        self.store_product.is_active = False
        self.store_product.save()
        url = reverse("admin:products_storeproduct_changelist")
        data = {
            "action": "active_product",
            "_selected_action": [self.store_product.pk],
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.store_product.refresh_from_db()
        self.assertTrue(self.store_product.is_active)

    def test_store_product_change_page(self):
        response = self.client.get(
            reverse(
                "admin:products_storeproduct_change",
                args=[self.store_product.pk]
            )
        )

        self.assertEqual(response.status_code, 200)
