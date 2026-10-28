from io import BytesIO

from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from apps.accounts.models import CustomUser, Store
from apps.orders.models import Order, OrderDetails
from apps.products.models import (
    Brand,
    Product,
    ProductGroup,
    StoreProduct,
)
from apps.warehouses.models import Warehouse, WarehouseType


class SellerAnalyticsDashboardViewTests(TestCase):

    def setUp(self):

        self.user = CustomUser.objects.create_user(
            mobile_number="09120000000",
            password="123456",
            name="Ali",
            family="Ahmadi",
        )

        self.user.is_active = True
        self.user.save()

        self.profile = self.user.userprofile

        self.store = Store.objects.create(
            user=self.user,
            store_name="Digital Shop",
            store_phone="09121111111",
        )

        self.brand = Brand.objects.create(
            brand_title="Samsung",
            image_name=self.create_test_image(),
        )

        self.product_group = ProductGroup.objects.create(
            group_title="Mobile",
            image_name=self.create_test_image(),
            slug="mobile",
        )

        self.product = Product.objects.create(
            product_name="Galaxy S25",
            image_name=self.create_test_image(),
            brand=self.brand,
            slug="galaxy-s25",
        )

        self.product.product_group.add(
            self.product_group
        )

        self.store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=50000000,
        )

        self.input_type = WarehouseType.objects.create(
            warehouse_type_title="ورود",
            code=WarehouseType.INPUT,
        )

        self.output_type = WarehouseType.objects.create(
            warehouse_type_title="خروج",
            code=WarehouseType.OUTPUT,
        )

        self.input_warehouse = Warehouse.objects.create(
            warehouse_type=self.input_type,
            user_registered=self.user,
            store_product=self.store_product,
            qty=20,
            price=45000000,
        )

        self.output_warehouse = Warehouse.objects.create(
            warehouse_type=self.output_type,
            user_registered=self.user,
            store_product=self.store_product,
            qty=5,
        )

        self.order = Order.objects.create(
            customer=self.profile,
            store=self.store,
            is_finally=True,
        )

        self.order_detail = OrderDetails.objects.create(
            order=self.order,
            store_product=self.store_product,
            qty=2,
            price=50000000,
        )

        self.product2 = Product.objects.create(
            product_name="Laptop",
            image_name=self.create_test_image(),
            brand=self.brand,
            slug="laptop",
        )

        self.product2.product_group.add(
            self.product_group
        )

        self.store_product2 = StoreProduct.objects.create(
            store=self.store,
            product=self.product2,
            price=30000000,
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

    def login(self):

        self.client.force_login(
            self.user
        )

    def test_dashboard_redirect_if_not_logged_in(self):

        response = self.client.get(
            reverse("analytics:seller_dashboard")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_dashboard_redirects_user_without_store(self):

        other = CustomUser.objects.create_user(
            mobile_number="09127777777",
            password="123456",
        )
        other.is_active = True
        other.save()

        self.client.force_login(other)

        response = self.client.get(
            reverse("analytics:seller_dashboard")
        )

        self.assertRedirects(
            response,
            reverse("accounts:create_store"),
            fetch_redirect_response=False,
        )

    def test_dashboard_view_logged_in(self):

        self.login()

        response = self.client.get(
            reverse("analytics:seller_dashboard")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_dashboard_context(self):

        self.login()

        response = self.client.get(
            reverse("analytics:seller_dashboard")
        )

        self.assertIn(
            "top_products",
            response.context,
        )

        self.assertIn(
            "orders_count",
            response.context,
        )

        self.assertIn(
            "profit",
            response.context,
        )

        self.assertIn(
            "top_customers",
            response.context,
        )

        self.assertIn(
            "daily_labels",
            response.context,
        )

        self.assertIn(
            "daily_values",
            response.context,
        )

        self.assertEqual(
            response.context["orders_count"],
            1,
        )

        self.assertEqual(
            response.context["profit"]["sell"],
            100000000,
        )

        self.assertEqual(
            response.context["profit"]["buy"],
            900000000,
        )

        self.assertEqual(
            response.context["profit"]["profit"],
            -800000000,
        )

    def test_dashboard_uses_correct_template(self):

        self.login()

        response = self.client.get(
            reverse("analytics:seller_dashboard")
        )

        self.assertTemplateUsed(
            response,
            "analytics/dashboard.html",
        )

    def test_reports_redirect_if_not_logged_in(self):

        response = self.client.get(
            reverse("analytics:reports")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_reports_view_logged_in(self):

        self.login()

        response = self.client.get(
            reverse("analytics:reports")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_reports_uses_correct_template(self):

        self.login()

        response = self.client.get(
            reverse("analytics:reports")
        )

        self.assertTemplateUsed(
            response,
            "analytics/reports.html",
        )

    def test_reports_context(self):

        self.login()

        response = self.client.get(
            reverse("analytics:reports")
        )

        self.assertIn(
            "pandas_summary",
            response.context,
        )

        self.assertIn(
            "sales_products",
            response.context,
        )

        self.assertIn(
            "pivot_table",
            response.context,
        )

        self.assertIn(
            "monthly_trend",
            response.context,
        )

        self.assertIn(
            "customer_segmentation",
            response.context,
        )

        self.assertIn(
            "forecast",
            response.context,
        )

    def test_export_excel_redirect_if_not_logged_in(self):

        response = self.client.get(
            reverse("analytics:export_excel")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_export_excel_logged_in(self):

        self.login()

        response = self.client.get(
            reverse("analytics:export_excel")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_export_excel_content_type(self):

        self.login()

        response = self.client.get(
            reverse("analytics:export_excel")
        )

        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_export_excel_filename(self):

        self.login()

        response = self.client.get(
            reverse("analytics:export_excel")
        )

        self.assertIn(
            "sales_report.xlsx",
            response["Content-Disposition"],
        )

    def test_pdf_redirect_if_not_logged_in(self):

        response = self.client.get(
            reverse("analytics:export_pdf")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_pdf_redirect(self):

        self.login()

        response = self.client.get(
            reverse("analytics:export_pdf")
        )

        self.assertRedirects(
            response,
            reverse("analytics:reports"),
        )

    def test_pdf_warning_message(self):

        self.login()

        response = self.client.get(
            reverse("analytics:export_pdf")
        )

        messages = list(
            get_messages(
                response.wsgi_request
            )
        )

        self.assertEqual(
            str(messages[0]),
            "امکان دانلود PDF در نسخه فعلی غیرفعال است.",
        )

