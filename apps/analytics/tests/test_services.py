from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from PIL import Image

from apps.accounts.models import CustomUser, Store
from apps.analytics.services import (
    get_active_products_count,
    get_available_products_count,
    get_average_order_amount,
    get_daily_sales,
    get_last_7_days_sales,
    get_last_orders,
    get_low_stock_products,
    get_monthly_income,
    get_new_customers_this_month,
    get_orders_count,
    get_products_without_sales,
    get_store_profit,
    get_today_sales,
    get_total_sales,
    get_top_categories,
    get_top_customers,
    get_top_products,
)
from apps.orders.models import Order, OrderDetails
from apps.products.models import (
    Brand,
    Product,
    ProductGroup,
    StoreProduct,
)
from apps.warehouses.models import Warehouse, WarehouseType


class AnalyticsServiceTests(TestCase):

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

    def test_get_total_sales(self):

        total = get_total_sales(
            self.store
        )

        self.assertEqual(
            total,
            100000000
        )

    def test_get_orders_count(self):

        count = get_orders_count(
            self.store
        )

        self.assertEqual(
            count,
            1
        )

    def test_get_top_products(self):

        result = get_top_products(
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
            result[0]["total_sales"],
            2
        )

    def test_get_today_sales(self):

        total = get_today_sales(
            self.store
        )

        self.assertEqual(
            total,
            100000000
        )

    def test_get_top_categories(self):

        categories = get_top_categories(
            self.store
        )

        self.assertEqual(
            len(categories),
            1
        )

        self.assertEqual(
            categories[0][
                "store_product__product__product_group__group_title"
            ],
            "Mobile"
        )

        self.assertEqual(
            categories[0]["total_sales"],
            2
        )

    def test_get_daily_sales(self):

        daily_sales = get_daily_sales(
            self.store
        )

        self.assertEqual(
            len(daily_sales),
            1
        )

        self.assertEqual(
            daily_sales[0][
                "order__register_date"
            ],
            timezone.now().date()
        )

        self.assertEqual(
            daily_sales[0]["total_sales"],
            100000000
        )

    def test_get_products_without_sales(self):

        products = get_products_without_sales(
            self.store
        )

        self.assertEqual(
            products.count(),
            1
        )

        self.assertEqual(
            products.first(),
            self.store_product2
        )

    def test_get_monthly_income(self):

        result = get_monthly_income(
            self.store
        )

        self.assertEqual(
            len(result),
            1
        )

        self.assertEqual(
            result[0]["income"],
            100000000
        )

        self.assertEqual(
            result[0]["month"].month,
            timezone.now().month
        )

        self.assertEqual(
            result[0]["month"].year,
            timezone.now().year
        )

    def test_get_low_stock_products(self):

        result = get_low_stock_products(
            self.store
        )

        self.assertEqual(
            len(result),
            1
        )

        self.assertEqual(
            result[0]["store_product"],
            self.store_product2
        )

        self.assertEqual(
            result[0]["qty"],
            0
        )

    def test_get_active_products_count(self):

        result = get_active_products_count(
            self.store
        )

        self.assertEqual(
            result,
            2
        )

    def test_get_available_products_count(self):

        result = get_available_products_count(
            self.store
        )

        self.assertEqual(
            result,
            1
        )

    def test_get_store_profit(self):

        result = get_store_profit(
            self.store
        )

        self.assertEqual(
            result["sell"],
            100000000
        )

        self.assertEqual(
            result["buy"],
            900000000
        )

        self.assertEqual(
            result["profit"],
            -800000000
        )

    def test_get_last_orders(self):

        result = get_last_orders(
            self.store
        )

        self.assertEqual(
            len(result),
            1
        )

        self.assertEqual(
            result.first(),
            self.order
        )

    def test_get_top_customers(self):

        result = get_top_customers(
            self.store
        )

        self.assertEqual(
            len(result),
            1
        )

        self.assertEqual(
            result[0][
                "order__customer__user__name"
            ],
            "Ali"
        )

        self.assertEqual(
            result[0][
                "order__customer__user__family"
            ],
            "Ahmadi"
        )

        self.assertEqual(
            result[0]["total_orders"],
            1
        )

        self.assertEqual(
            result[0]["total_amount"],
            100000000
        )

    def test_get_new_customers_this_month(self):

        result = get_new_customers_this_month(
            self.store
        )

        self.assertEqual(
            result,
            1
        )

    def test_get_average_order_amount(self):

        result = get_average_order_amount(
            self.store
        )

        self.assertEqual(
            result,
            100000000
        )

    def test_get_last_7_days_sales(self):

        result = get_last_7_days_sales(
            self.store
        )

        self.assertEqual(
            len(result),
            7
        )

        today = timezone.now().date()

        today_result = next(
            item
            for item in result
            if item["date"] == today
        )

        self.assertEqual(
            today_result["amount"],
            self.order_detail.price
            * self.order_detail.qty
        )