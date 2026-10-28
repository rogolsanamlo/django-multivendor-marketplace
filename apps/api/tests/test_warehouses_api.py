from io import BytesIO
import uuid

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

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
from apps.warehouses.models import (
    Warehouse,
    WarehouseType,
)


class WarehouseAPITests(APITestCase):

    def setUp(self):

        self.user = self.create_user(
            "09120000001"
        )

        self.other_user = self.create_user(
            "09120000002"
        )

        self.store = self.create_store(
            self.user,
            "09120000011"
        )

        self.other_store = self.create_store(
            self.other_user,
            "09120000022"
        )

        self.warehouse_type = WarehouseType.objects.create(
            warehouse_type_title="ورودی",
            code=WarehouseType.INPUT,
        )

        self.output_type = WarehouseType.objects.create(
            warehouse_type_title="خروجی",
            code=WarehouseType.OUTPUT,
        )

        self.store_product = self.create_store_product(
            self.store
        )

        self.other_store_product = (
            self.create_store_product(
                self.other_store
            )
        )

        self.warehouse = Warehouse.objects.create(
            warehouse_type=self.warehouse_type,
            user_registered=self.user,
            store_product=self.store_product,
            qty=10,
            price=100000,
        )

        self.other_warehouse = Warehouse.objects.create(
            warehouse_type=self.warehouse_type,
            user_registered=self.other_user,
            store_product=self.other_store_product,
            qty=20,
            price=200000,
        )

    def create_user(self, mobile):

        return CustomUser.objects.create_user(
            mobile_number=mobile,
            password="test123",
            email=f"{mobile}@example.com",
            name="Test",
            family="User",
        )

    def create_store(self, user, phone):

        return Store.objects.create(
            user=user,
            store_name=f"Store {phone}",
            store_phone=phone,
            address="Test Address",
            is_active=True,
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

    def create_store_product(self, store):

        brand = Brand.objects.create(
            brand_title="Test Brand",
            image_name=self.create_test_image(),
            slug=f"test-brand-{uuid.uuid4().hex[:10]}",
        )

        product_group = ProductGroup.objects.create(
            group_title="Test Group",
            image_name=self.create_test_image(),
            slug=f"test-group-{uuid.uuid4().hex[:10]}",
        )

        product = Product.objects.create(
            product_name=f"Product {store.id}",
            image_name=self.create_test_image(),
            brand=brand,
            slug=f"product-{store.id}",
        )

        product.product_group.add(
            product_group
        )

        return StoreProduct.objects.create(
            store=store,
            product=product,
            price=100000,
        )

    def test_unauthenticated_user_cannot_see_warehouse_types(
        self
    ):

        url = reverse(
            "api:warehouse-type-list"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_see_warehouse_types(
        self
    ):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:warehouse-type-list"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

    def test_warehouse_type_api_is_read_only(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:warehouse-type-list"
        )

        response = self.client.post(
            url,
            {
                "warehouse_type_title": "Test",
                "code": "test",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_unauthenticated_user_cannot_see_warehouses(
        self
    ):

        url = reverse(
            "api:warehouse-list"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_store_owner_can_see_own_warehouses(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:warehouse-list"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            self.warehouse.id,
        )

    def test_store_owner_cannot_see_other_store_warehouse(
        self
    ):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:warehouse-detail",
            kwargs={
                "pk": self.other_warehouse.id
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_store_owner_can_create_warehouse(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:warehouse-list"
        )

        response = self.client.post(
            url,
            {
                "warehouse_type": self.warehouse_type.id,
                "store_product": self.store_product.id,
                "qty": 15,
                "price": 150000,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["qty"],
            15,
        )

        self.assertEqual(
            response.data["user_registered"],
            self.user.id,
        )

    def test_store_owner_cannot_create_warehouse_for_other_store(
        self
    ):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:warehouse-list"
        )

        response = self.client.post(
            url,
            {
                "warehouse_type": self.warehouse_type.id,
                "store_product": self.other_store_product.id,
                "qty": 10,
                "price": 100000,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_cannot_set_another_user_as_registered_user(
        self
    ):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:warehouse-list"
        )

        response = self.client.post(
            url,
            {
                "warehouse_type": self.warehouse_type.id,
                "store_product": self.store_product.id,
                "user_registered": self.other_user.id,
                "qty": 10,
                "price": 100000,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        warehouse = Warehouse.objects.latest(
            "id"
        )

        self.assertEqual(
            warehouse.user_registered,
            self.user,
        )

    def test_warehouse_qty_must_be_positive(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:warehouse-list"
        )

        response = self.client.post(
            url,
            {
                "warehouse_type": self.warehouse_type.id,
                "store_product": self.store_product.id,
                "qty": 0,
                "price": 100000,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_warehouse_api_does_not_allow_update(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:warehouse-detail",
            kwargs={
                "pk": self.warehouse.id
            },
        )

        response = self.client.put(
            url,
            {
                "warehouse_type": self.output_type.id,
                "store_product": self.store_product.id,
                "qty": 100,
                "price": 500000,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_warehouse_api_does_not_allow_patch(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:warehouse-detail",
            kwargs={
                "pk": self.warehouse.id
            },
        )

        response = self.client.patch(
            url,
            {
                "qty": 100
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_store_owner_can_delete_own_warehouse(self):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:warehouse-detail",
            kwargs={
                "pk": self.warehouse.id
            },
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Warehouse.objects.filter(
                pk=self.warehouse.id
            ).exists()
        )

    def test_store_owner_cannot_delete_other_store_warehouse(
        self
    ):

        self.client.force_authenticate(
            user=self.user
        )

        url = reverse(
            "api:warehouse-detail",
            kwargs={
                "pk": self.other_warehouse.id
            },
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )