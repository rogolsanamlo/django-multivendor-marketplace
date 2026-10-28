"""
Fill the database with a small, believable demo catalog.

    python manage.py seed_demo

Creates product groups and sub-groups, brands, products (with generated
pictures), two demo stores with their own prices and stock. It is safe to run
more than once: existing records are reused, nothing is duplicated.
"""
import hashlib
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from PIL import Image, ImageDraw

from apps.accounts.models import CustomUser, Store
from apps.products.models import Brand, Product, ProductGroup, StoreProduct
from apps.warehouses.models import Warehouse, WarehouseType
from utils import generate_unique_slug

DEMO_PASSWORD = "demo12345"

GROUPS = [
    ("لوازم دیجیتال", ["گوشی موبایل", "لپ‌تاپ"]),
    ("پوشاک", ["لباس مردانه", "لباس زنانه"]),
    ("لبنیات و خوراکی", ["لبنیات", "تنقلات"]),
]

BRANDS = ["نوین", "آرمان", "سپهر", "پارسا"]

# slug, name, sub-group, brand, base price (toman)
PRODUCTS = [
    ("demo-phone-alpha", "گوشی هوشمند مدل آلفا ۱۲۸ گیگابایت", "گوشی موبایل", "نوین", 14500000),
    ("demo-phone-beta", "گوشی هوشمند مدل بتا ۲۵۶ گیگابایت", "گوشی موبایل", "آرمان", 21900000),
    ("demo-laptop-sigma", "لپ‌تاپ مدل سیگما ۱۵ اینچ", "لپ‌تاپ", "سپهر", 38900000),
    ("demo-laptop-delta", "لپ‌تاپ مدل دلتا ۱۴ اینچ", "لپ‌تاپ", "نوین", 32500000),
    ("demo-shirt-men", "پیراهن مردانه نخی", "لباس مردانه", "پارسا", 890000),
    ("demo-jacket-men", "کاپشن مردانه زمستانی", "لباس مردانه", "آرمان", 2450000),
    ("demo-scarf-women", "شال زنانه نخی", "لباس زنانه", "پارسا", 420000),
    ("demo-coat-women", "مانتو زنانه تابستانی", "لباس زنانه", "سپهر", 1350000),
    ("demo-butter", "کره پاستوریزه ۱۰۰ گرمی", "لبنیات", "پارسا", 42000),
    ("demo-yogurt", "ماست پرچرب ۹۰۰ گرمی", "لبنیات", "نوین", 68000),
    ("demo-chips", "چیپس نمکی ۱۰۰ گرمی", "تنقلات", "آرمان", 35000),
    ("demo-nuts", "آجیل مخلوط ۵۰۰ گرمی", "تنقلات", "سپهر", 290000),
]

# mobile, name, family, store phone, store name, price factor, every n-th product
SELLERS = [
    ("09120000001", "فروشنده", "اول", "02100000001", "فروشگاه نمونه آلفا", 1.00, 1),
    ("09120000002", "فروشنده", "دوم", "02100000002", "فروشگاه نمونه بتا", 1.08, 2),
]


def make_image(seed, size=600):
    """A simple generated picture (gradient + shapes), no text and no assets."""
    digest = hashlib.md5(seed.encode("utf-8")).digest()

    top = (90 + digest[0] % 120, 90 + digest[1] % 120, 90 + digest[2] % 120)
    bottom = (60 + digest[3] % 120, 60 + digest[4] % 120, 60 + digest[5] % 120)

    image = Image.new("RGB", (size, size))
    draw = ImageDraw.Draw(image)

    for y in range(size):
        ratio = y / size
        color = tuple(int(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3))
        draw.line([(0, y), (size, y)], fill=color)

    accent = (255, 255, 255)
    draw.ellipse(
        [size * 0.28, size * 0.28, size * 0.72, size * 0.72],
        outline=accent,
        width=size // 40,
    )
    draw.rectangle(
        [size * 0.40, size * 0.40, size * 0.60, size * 0.60],
        fill=accent,
    )

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    return ContentFile(buffer.getvalue())


def round_price(value):
    """Round a toman price to the nearest thousand."""
    return int(round(value / 1000.0)) * 1000


class Command(BaseCommand):
    help = "Create a small demo catalog (groups, brands, products, stores, stock)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Allow running while DEBUG is off.",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG and not options["force"]:
            raise CommandError(
                "seed_demo creates demo accounts with a known password, so it "
                "only runs while DEBUG is on. Use --force to override."
            )

        sub_groups = self.create_groups()
        brands = self.create_brands()
        products = self.create_products(sub_groups, brands)
        stores = self.create_stores()
        self.create_listings(stores, products)

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write("Demo sellers (password: %s):" % DEMO_PASSWORD)

        for mobile, _name, _family, _phone, store_name, _factor, _step in SELLERS:
            self.stdout.write("  %s  ->  %s" % (mobile, store_name))

    def create_groups(self):
        sub_groups = {}

        for root_title, children in GROUPS:
            root = self.get_or_create_group(root_title, None)

            for child_title in children:
                sub_groups[child_title] = self.get_or_create_group(child_title, root)

        return sub_groups

    def get_or_create_group(self, title, parent):
        group = ProductGroup.objects.filter(
            group_title=title,
            group_parent=parent,
        ).first()

        if group is None:
            group = ProductGroup(
                group_title=title,
                group_parent=parent,
                slug=generate_unique_slug(ProductGroup, "", "group"),
            )
            group.image_name.save(
                "demo.png",
                make_image("group-" + title),
                save=False,
            )
            group.save()

        return group

    def create_brands(self):
        brands = {}

        for title in BRANDS:
            brand = Brand.objects.filter(brand_title=title).first()

            if brand is None:
                brand = Brand(
                    brand_title=title,
                    slug=generate_unique_slug(Brand, "", "brand"),
                )
                brand.image_name.save(
                    "demo.png",
                    make_image("brand-" + title),
                    save=False,
                )
                brand.save()

            brands[title] = brand

        return brands

    def create_products(self, sub_groups, brands):
        products = []

        for slug, name, group_title, brand_title, base_price in PRODUCTS:
            product = Product.objects.filter(slug=slug).first()

            if product is None:
                product = Product(
                    slug=slug,
                    product_name=name,
                    brand=brands[brand_title],
                    summary_description="کالای نمونه برای نمایش امکانات سایت",
                    description="<p>%s؛ این کالا فقط برای نمایش امکانات سایت ساخته شده است.</p>" % name,
                )
                product.image_name.save(
                    "demo.png",
                    make_image(slug),
                    save=False,
                )
                product.save()
                product.product_group.add(sub_groups[group_title])

            products.append((product, base_price))

        return products

    def create_stores(self):
        stores = []

        for mobile, name, family, phone, store_name, factor, step in SELLERS:
            user = CustomUser.objects.filter(mobile_number=mobile).first()

            if user is None:
                user = CustomUser.objects.create_user(
                    mobile_number=mobile,
                    name=name,
                    family=family,
                    password=DEMO_PASSWORD,
                )

            if not user.is_active:
                user.is_active = True
                user.save()

            store = Store.objects.filter(user=user).first()

            if store is None:
                store = Store.objects.create(
                    user=user,
                    store_name=store_name,
                    store_phone=phone,
                    address="تهران",
                    description="فروشگاه نمونه",
                )

            if not store.is_active:
                store.is_active = True
                store.save()

            stores.append((store, factor, step))

        return stores

    def create_listings(self, stores, products):
        input_type, _ = WarehouseType.objects.get_or_create(
            code="input",
            defaults={"warehouse_type_title": "ورود به انبار"},
        )

        for store, factor, step in stores:
            for index, (product, base_price) in enumerate(products):
                if index % step:
                    continue

                store_product, created = StoreProduct.objects.get_or_create(
                    store=store,
                    product=product,
                    defaults={"price": round_price(base_price * factor)},
                )

                has_stock_records = Warehouse.objects.filter(
                    store_product=store_product
                ).exists()

                if not has_stock_records:
                    Warehouse.objects.create(
                        warehouse_type=input_type,
                        user_registered=store.user,
                        store_product=store_product,
                        qty=5 + (index * 7) % 40,
                    )
