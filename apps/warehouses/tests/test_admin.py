import json

from django.test import RequestFactory

from apps.products.models import (
    Brand,
    Product,
    ProductGroup,
    StoreProduct,
)
from apps.tests.base import BaseAccountTest
from apps.warehouses.admin import export_json
from apps.warehouses.models import Warehouse, WarehouseType


class WarehouseAdminTest(BaseAccountTest):

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

    def test_export_json_action(self):
        request = RequestFactory().get(
            "/admin/warehouses/warehouse/"
        )

        queryset = Warehouse.objects.filter(
            id=self.warehouse.id
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

        data = json.loads(
            response.content
        )

        self.assertEqual(
            len(data),
            1,
        )

        self.assertEqual(
            data[0]["model"],
            "warehouses.warehouse",
        )

        self.assertEqual(
            data[0]["fields"]["qty"],
            10,
        )

        self.assertEqual(
            data[0]["fields"]["price"],
            100000,
        )

