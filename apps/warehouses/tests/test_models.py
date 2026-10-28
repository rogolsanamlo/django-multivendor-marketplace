from django.test import TestCase

from apps.accounts.models import (
    CustomUser,
    Store,
)
from apps.products.models import (
    Brand,
    Product,
    ProductGroup,
    StoreProduct,
)
from apps.tests.base import BaseAccountTest
from apps.warehouses.models import (
    Warehouse,
    WarehouseType,
)


class WarehouseModelTest(BaseAccountTest):

    def setUp(self):
        super().setUp()

        self.brand = Brand.objects.create(
            brand_title="Test Brand",
            slug="test-brand",
            image_name=self.create_test_image(),
        )

        self.product_group = ProductGroup.objects.create(
            group_title="Test Group",
            slug="test-group",
            image_name=self.create_test_image(),
        )

        self.product = Product.objects.create(
            product_name="Test Product",
            brand=self.brand,
            slug="test-product",
            image_name=self.create_test_image(),
        )

        self.product.product_group.add(
            self.product_group
        )

        self.store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=100000,
        )

        self.warehouse_type = WarehouseType.objects.create(
            warehouse_type_title="Input",
            code=WarehouseType.INPUT,
        )

        self.warehouse = Warehouse.objects.create(
            warehouse_type=self.warehouse_type,
            user_registered=self.user,
            store_product=self.store_product,
            qty=10,
            price=100000,
        )

    def test_warehouse_type(self):
        self.assertEqual(
            self.warehouse.warehouse_type,
            self.warehouse_type,
        )

    def test_user_registered(self):
        self.assertEqual(
            self.warehouse.user_registered,
            self.user,
        )

    def test_store_product(self):
        self.assertEqual(
            self.warehouse.store_product,
            self.store_product,
        )

    def test_warehouse_qty(self):
        self.assertEqual(
            self.warehouse.qty,
            10,
        )

    def test_warehouse_price(self):
        self.assertEqual(
            self.warehouse.price,
            100000,
        )

    def test_warehouse_register_date(self):
        self.assertIsNotNone(
            self.warehouse.register_date,
        )

    def test_warehouse_str(self):
        expected = (
            f"{self.warehouse.warehouse_type}-"
            f"{self.warehouse.store_product}"
        )

        self.assertEqual(
            str(self.warehouse),
            expected,
        )

    def test_delete_warehouse_type_deletes_warehouse(self):
        warehouse_id = self.warehouse.id

        self.warehouse_type.delete()

        self.assertFalse(
            Warehouse.objects.filter(
                id=warehouse_id
            ).exists()
        )

    def test_delete_user_deletes_warehouse(self):
        warehouse_id = self.warehouse.id

        self.user.delete()

        self.assertFalse(
            Warehouse.objects.filter(
                id=warehouse_id
            ).exists()
        )

    def test_delete_store_product_deletes_warehouse(self):
        warehouse_id = self.warehouse.id

        self.store_product.delete()

        self.assertFalse(
            Warehouse.objects.filter(
                id=warehouse_id
            ).exists()
        )

    def test_store_product_can_access_warehouse_products(self):
        warehouse = (
            self.store_product
            .warehouse_products
            .first()
        )

        self.assertEqual(
            warehouse,
            self.warehouse,
        )

    def test_store_product_can_access_all_warehouse_products(self):
        second_warehouse = Warehouse.objects.create(
            warehouse_type=self.warehouse_type,
            user_registered=self.user,
            store_product=self.store_product,
            qty=5,
            price=100000,
        )

        warehouses = (
            self.store_product
            .warehouse_products
            .all()
        )

        self.assertEqual(
            warehouses.count(),
            2,
        )

        self.assertIn(
            self.warehouse,
            warehouses,
        )

        self.assertIn(
            second_warehouse,
            warehouses,
        )

    def test_warehouse_price_can_be_none(self):
        warehouse = Warehouse.objects.create(
            warehouse_type=self.warehouse_type,
            user_registered=self.user,
            store_product=self.store_product,
            qty=10,
            price=None,
        )

        self.assertIsNone(
            warehouse.price,
        )

    def test_warehouse_qty_can_be_zero(self):
        warehouse = Warehouse.objects.create(
            warehouse_type=self.warehouse_type,
            user_registered=self.user,
            store_product=self.store_product,
            qty=0,
            price=100000,
        )

        self.assertEqual(
            warehouse.qty,
            0,
        )


class WarehouseTypeModelTest(TestCase):

    def test_warehouse_type_str(self):
        warehouse_type = WarehouseType.objects.create(
            warehouse_type_title="Input",
            code=WarehouseType.INPUT,
        )

        self.assertEqual(
            str(warehouse_type),
            "Input",
        )

    def test_warehouse_type_title(self):
        warehouse_type = WarehouseType.objects.create(
            warehouse_type_title="Output",
            code=WarehouseType.OUTPUT,
        )

        self.assertEqual(
            warehouse_type.warehouse_type_title,
            "Output",
        )


class StoreProductWarehouseTest(BaseAccountTest):

    def setUp(self):
        super().setUp()

        self.brand = Brand.objects.create(
            brand_title="Test Brand",
            slug="test-brand",
            image_name=self.create_test_image(),
        )

        self.product_group = ProductGroup.objects.create(
            group_title="Test Group",
            slug="test-group",
            image_name=self.create_test_image(),
        )

        self.product = Product.objects.create(
            product_name="Test Product",
            brand=self.brand,
            slug="test-product",
            image_name=self.create_test_image(),
        )

        self.product.product_group.add(
            self.product_group
        )

        self.store_product = StoreProduct.objects.create(
            store=self.store,
            product=self.product,
            price=100000,
        )

        self.input_type = WarehouseType.objects.create(
            warehouse_type_title="Input",
            code=WarehouseType.INPUT,
        )

        self.output_type = WarehouseType.objects.create(
            warehouse_type_title="Output",
            code=WarehouseType.OUTPUT,
        )

    def test_number_in_warehouse_with_input(self):
        Warehouse.objects.create(
            warehouse_type=self.input_type,
            user_registered=self.user,
            store_product=self.store_product,
            qty=10,
            price=100000,
        )

        self.assertEqual(
            self.store_product.get_number_in_warehouse(),
            10,
        )

    def test_number_in_warehouse_with_input_and_output(self):
        Warehouse.objects.create(
            warehouse_type=self.input_type,
            user_registered=self.user,
            store_product=self.store_product,
            qty=10,
            price=100000,
        )

        Warehouse.objects.create(
            warehouse_type=self.output_type,
            user_registered=self.user,
            store_product=self.store_product,
            qty=3,
            price=100000,
        )

        self.assertEqual(
            self.store_product.get_number_in_warehouse(),
            7,
        )

    def test_number_in_warehouse_with_no_warehouse(self):
        self.assertEqual(
            self.store_product.get_number_in_warehouse(),
            0,
        )

    def test_number_in_warehouse_with_multiple_inputs_and_outputs(self):
        Warehouse.objects.create(
            warehouse_type=self.input_type,
            user_registered=self.user,
            store_product=self.store_product,
            qty=10,
            price=100000,
        )

        Warehouse.objects.create(
            warehouse_type=self.input_type,
            user_registered=self.user,
            store_product=self.store_product,
            qty=5,
            price=100000,
        )

        Warehouse.objects.create(
            warehouse_type=self.output_type,
            user_registered=self.user,
            store_product=self.store_product,
            qty=3,
            price=100000,
        )

        Warehouse.objects.create(
            warehouse_type=self.output_type,
            user_registered=self.user,
            store_product=self.store_product,
            qty=2,
            price=100000,
        )

        self.assertEqual(
            self.store_product.get_number_in_warehouse(),
            10,
        )

    def test_warehouse_quantity_is_separated_between_store_products(self):
        second_user = CustomUser.objects.create_user(
            mobile_number="09123333333",
            password="123456",
            name="Reza",
            family="Ahmadi",
            email="reza@test.com",
        )

        second_store = Store.objects.create(
            user=second_user,
            store_name="Second Shop",
            store_phone="09124444444",
        )

        second_store_product = StoreProduct.objects.create(
            store=second_store,
            product=self.product,
            price=120000,
        )

        Warehouse.objects.create(
            warehouse_type=self.input_type,
            user_registered=self.user,
            store_product=self.store_product,
            qty=10,
            price=100000,
        )

        Warehouse.objects.create(
            warehouse_type=self.input_type,
            user_registered=second_user,
            store_product=second_store_product,
            qty=20,
            price=120000,
        )

        self.assertEqual(
            self.store_product.get_number_in_warehouse(),
            10,
        )

        self.assertEqual(
            second_store_product.get_number_in_warehouse(),
            20,
        )