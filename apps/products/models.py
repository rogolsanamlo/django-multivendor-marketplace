from django.db import models
from django.db.models import Avg, Sum
from django.urls import reverse
from django.utils import timezone

from ckeditor_uploader.fields import RichTextUploadingField

from apps.accounts.models import Store
from utils import FileUpload


class Brand(models.Model):
    brand_title = models.CharField(
        max_length=50,
        verbose_name='نام برند'
    )
    file_upload = FileUpload('images', 'brand')
    image_name = models.ImageField(
        upload_to=file_upload,
        verbose_name='تصویر برند کالا'
    )
    slug = models.SlugField(
        max_length=200,
        blank=True,
        unique=True
    )

    def __str__(self):
        return self.brand_title

    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برند ها'


class ProductGroup(models.Model):
    group_title = models.CharField(
        max_length=100,
        verbose_name='عنوان گروه کالا'
    )
    file_upload = FileUpload('images', 'product_group')
    image_name = models.ImageField(
        upload_to=file_upload,
        verbose_name='تصویر کالا'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال/غیر فعال'
    )
    group_parent = models.ForeignKey(
        'ProductGroup',
        on_delete=models.PROTECT,
        verbose_name='والد گروه کالا',
        blank=True,
        null=True,
        related_name='groups'
    )
    slug = models.SlugField(
        unique=True
    )
    register_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ درج'
    )
    published_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='تاریخ انتشار'
    )
    update_date = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ اخرین به روزرسانی'
    )

    def __str__(self):
        return self.group_title

    class Meta:
        verbose_name = 'گروه کالا'
        verbose_name_plural = 'گروه های کالا'


class Feature(models.Model):
    feature_name = models.CharField(
        max_length=100,
        verbose_name='نام ویژگی'
    )
    product_group = models.ManyToManyField(
        ProductGroup,
        verbose_name='گروه کالا',
        related_name='features_of_groups'
    )

    def __str__(self):
        return self.feature_name

    class Meta:
        verbose_name = 'ویژگی'
        verbose_name_plural = 'ویژگی ها'


class FeatureValue(models.Model):
    value_title = models.CharField(
        max_length=100,
        verbose_name='عنوان مقدار'
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        verbose_name='ویژگی',
        related_name='feature_values'
    )

    def __str__(self):
        return f"{self.id}-{self.value_title}"

    class Meta:
        verbose_name = 'مقدار ویژگی'
        verbose_name_plural = 'مقادیر ویژگی ها'


class Product(models.Model):
    product_name = models.CharField(
        max_length=200,
        verbose_name='نام کالا'
    )
    file_upload = FileUpload('images', 'product')
    image_name = models.ImageField(
        upload_to=file_upload,
        verbose_name='تصویر کالا'
    )
    product_group = models.ManyToManyField(
        ProductGroup,
        verbose_name='گروه کالا',
        related_name='products_of_groups'
    )
    brand = models.ForeignKey(
        'Brand',
        on_delete=models.PROTECT,
        verbose_name='برند کالا',
        related_name='products_of_brands'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال/غیر فعال'
    )
    slug = models.SlugField(
        max_length=200,
        null=False,
        blank=False,
        unique=True
    )
    features = models.ManyToManyField(
        Feature,
        through='ProductFeature'
    )
    summary_description = models.TextField(
        blank=True,
        default=""
    )
    description = RichTextUploadingField(
        config_name='special',
        blank=True
    )
    register_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ درج'
    )
    update_date = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ اخرین به روزرسانی'
    )

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name = 'کالا'
        verbose_name_plural = 'کالا ها'


class StoreProduct(models.Model):
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        verbose_name='فروشگاه',
        related_name='products'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='کالا',
        related_name='store_products'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='قیمت کالا'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال/غیر فعال'
    )
    register_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ درج'
    )
    update_date = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ اخرین به روزرسانی'
    )

    class Meta:
        verbose_name = 'کالای فروشگاه'
        verbose_name_plural = 'کالاهای فروشگاه‌ها'
        unique_together = ('store', 'product')

    def get_absolute_url(self):
        return reverse(
            "products:product_details",
            kwargs={
                "pk": self.pk,
            },
        )

    def __str__(self):
        return f"{self.store} - {self.product}"

    def get_number_in_warehouse(self):
        input_qty = self.warehouse_products.filter(
            warehouse_type__code='input'
        ).aggregate(
            Sum('qty')
        )['qty__sum'] or 0

        output_qty = self.warehouse_products.filter(
            warehouse_type__code='output'
        ).aggregate(
            Sum('qty')
        )['qty__sum'] or 0

        return input_qty - output_qty

    def get_average_score(self):
        avg_score = self.scoring_product.all().aggregate(
            Avg('score')
        )['score__avg']

        if avg_score is None:
            avg_score = 0

        return avg_score

    @property
    def comments_count(self):
        """Number of approved comments (replies included)."""
        return self.comments.filter(is_active=True).count()

    @property
    def rating_stars(self):
        """Five booleans, True for each star that should be filled."""
        rounded = int(float(self.get_average_score()) + 0.5)

        return [position <= rounded for position in range(1, 6)]


class ProductFeature(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='کالا',
        related_name='product_feature'
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        verbose_name='ویژگی'
    )
    value = models.CharField(
        max_length=100,
        verbose_name='مقدار ویژگی کالا'
    )
    filter_value = models.ForeignKey(
        FeatureValue,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='ویژگی برای فیلتر'
    )

    def __str__(self):
        return f"{self.product}-{self.feature}:{self.value}"

    class Meta:
        verbose_name = 'ویژگی محصول'
        verbose_name_plural = 'ویژگی های محصولات'


class ProductGallery(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='کالا',
        related_name='gallery_images'
    )
    file_upload = FileUpload('images', 'product_gallery')
    image_name = models.ImageField(
        upload_to=file_upload,
        verbose_name='تصویر کالا'
    )

    class Meta:
        verbose_name = 'تصویر'
        verbose_name_plural = 'گالری تصاویر'