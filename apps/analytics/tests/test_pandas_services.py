from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from PIL import Image

from apps.accounts.models import CustomUser, Store
from apps.analytics.pandas_services import (
    abc_analysis,
    customer_segmentation,
    monthly_trend_dataframe,
    sales_by_product,
    sales_dataframe,
    sales_forecast,
    sales_growth_analysis,
    sales_pivot_table,
    weekday_sales_analysis,
)
from apps.orders.models import Order, OrderDetails
from apps.products.models import (
    Brand,
    Product,
    ProductGroup,
    StoreProduct,
)
from apps.warehouses.models import Warehouse, WarehouseType


class PandasServiceTests(TestCase):

    def setUp(self):

        self.user = CustomUser.objects.create_user(
            mobile_number="09120000000",
            password="123456",
            name="Ali",
            family="Ahmadi",
        )

        self.profile = self.user.userprofile

        self.store = Store.objects.create(
            user=self.user,
            store_name="Digital Shop",
            store_phone="09121111111",
        )

        self.image = self.create_test_image()

        self.brand = Brand.objects.create(
            brand_title="Samsung",
            image_name=self.image,
        )

        self.product_group = ProductGroup.objects.create(
            group_title="Mobile",
            image_name=self.image,
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
            warehouse_type_title="ورودی",
            code=WarehouseType.INPUT,
        )

        self.output_type = WarehouseType.objects.create(
            warehouse_type_title="خروجی",
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

    def test_sales_dataframe(self):

        result = sales_dataframe(self.store)

        self.assertFalse(
            result["dataframe"].empty
        )

        self.assertEqual(
            result["total_sales"],
            100000000
        )

        self.assertEqual(
            result["average_sales"],
            100000000
        )

        self.assertEqual(
            result["max_sale"],
            100000000
        )

        self.assertEqual(
            result["min_sale"],
            100000000
        )

    def test_sales_by_product(self):

        result = sales_by_product(
            self.store
        )

        self.assertFalse(
            result.empty
        )

        self.assertEqual(
            len(result),
            1
        )

        self.assertEqual(
            result.iloc[0][
                "store_product__product__product_name"
            ],
            "Galaxy S25"
        )

        self.assertEqual(
            result.iloc[0]["total_price"],
            100000000
        )

    def test_sales_pivot_table(self):

        result = sales_pivot_table(
            self.store
        )

        self.assertEqual(
            len(result),
            1
        )

        self.assertEqual(
            result[0][
                "store_product__product__product_name"
            ],
            "Galaxy S25"
        )

        month_column = [
            key
            for key in result[0].keys()
            if key != (
                "store_product__product__product_name"
            )
        ][0]

        self.assertEqual(
            result[0][month_column],
            100000000
        )

    def test_monthly_trend_dataframe(self):

        result = monthly_trend_dataframe(
            self.store
        )

        self.assertEqual(
            len(result),
            1
        )

        self.assertEqual(
            result[0]["total_price"],
            100000000
        )

        self.assertEqual(
            result[0]["month"],
            timezone.now().strftime("%Y-%m")
        )

    def test_abc_analysis(self):

        result = abc_analysis(
            self.store
        )

        self.assertEqual(
            len(result),
            1
        )

        self.assertEqual(
            result[0][
                "store_product__product__product_name"
            ],
            "Galaxy S25"
        )

        self.assertEqual(
            result[0]["total_price"],
            100000000
        )

        self.assertEqual(
            result[0]["percent"],
            100
        )

        self.assertEqual(
            result[0]["cumulative"],
            100
        )

        self.assertEqual(
            result[0]["class"],
            "C"
        )

    def test_customer_segmentation(self):

        result = customer_segmentation(
            self.store
        )

        self.assertEqual(
            len(result),
            1
        )

        self.assertEqual(
            result[0]["name"],
            "Ali"
        )

        self.assertEqual(
            result[0]["family"],
            "Ahmadi"
        )

        self.assertEqual(
            result[0]["total_orders"],
            1
        )

        self.assertEqual(
            result[0]["total_purchase"],
            100000000
        )

        self.assertEqual(
            result[0]["average_purchase"],
            100000000
        )

    def test_weekday_sales_analysis(self):

        result = weekday_sales_analysis(
            self.store
        )

        self.assertEqual(
            len(result),
            1
        )

        week_days = {
            0: "دوشنبه",
            1: "سه‌شنبه",
            2: "چهارشنبه",
            3: "پنجشنبه",
            4: "جمعه",
            5: "شنبه",
            6: "یکشنبه",
        }

        expected_day = week_days[
            timezone.now().weekday()
        ]

        self.assertEqual(
            result[0]["weekday"],
            expected_day
        )

        self.assertEqual(
            result[0]["total_price"],
            100000000
        )

    def test_sales_growth_analysis(self):

        result = sales_growth_analysis(
            self.store
        )

        self.assertEqual(
            len(result),
            1
        )

        self.assertEqual(
            result[0]["total_price"],
            100000000
        )

        self.assertEqual(
            result[0]["growth_percent"],
            0
        )

        self.assertEqual(
            result[0]["month"],
            timezone.now().strftime("%Y-%m")
        )

    def test_sales_forecast(self):

        result = sales_forecast(
            self.store
        )

        self.assertEqual(
            result["forecast"],
            100000000
        )