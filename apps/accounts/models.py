from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.text import slugify

from utils import FileUpload


class CustomUserManager(BaseUserManager):
    def create_user(
        self,
        mobile_number,
        email="",
        name="",
        family="",
        active_code=None,
        password=None,
    ):
        if not mobile_number:
            raise ValueError("شماره موبایل باید وارد شود")

        user = self.model(
            mobile_number=mobile_number,
            email=self.normalize_email(email),
            name=name,
            family=family,
            active_code=active_code,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        mobile_number,
        email,
        name,
        family,
        password=None,
        active_code=None,
    ):
        user = self.create_user(
            mobile_number=mobile_number,
            email=email,
            name=name,
            family=family,
            active_code=active_code,
            password=password,
        )

        user.is_active = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(
        "نام",
        max_length=50,
        blank=True,
    )
    email = models.EmailField(
        "ایمیل",
        max_length=200,
        blank=True,
    )
    mobile_number = models.CharField(
        "موبایل",
        max_length=11,
        unique=True,
    )
    family = models.CharField(
        "نام خانوادگی",
        max_length=50,
        blank=True,
    )

    register_date = models.DateField(
        "تاریخ ثبت‌نام",
        auto_now_add=True,
    )
    is_active = models.BooleanField(
        "فعال",
        default=False,
    )
    active_code = models.CharField(
        "کد فعال‌سازی",
        max_length=100,
        blank=True,
        null=True,
    )
    is_admin = models.BooleanField(
        "مدیر",
        default=False,
    )

    USERNAME_FIELD = "mobile_number"
    REQUIRED_FIELDS = ["email", "name", "family"]

    objects = CustomUserManager()

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self):
        return self.name + " " + self.family

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'


class UserProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name="کاربر",
    )
    address = models.TextField(
        "آدرس",
        null=True,
        blank=True,
    )

    file_upload = FileUpload("images", "customer")

    image_name = models.ImageField(
        "تصویر پروفایل",
        upload_to=file_upload,
        null=True,
        blank=True,
    )

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'پروفایل کاربر'
        verbose_name_plural = 'پروفایل‌های کاربران'


class Store(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="store",
        verbose_name="کاربر",
    )
    store_name = models.CharField(
        "نام فروشگاه",
        max_length=50,
        blank=False,
    )
    store_phone = models.CharField(
        "شماره فروشگاه",
        max_length=11,
        unique=True,
    )
    address = models.TextField(
        "آدرس",
        null=True,
        blank=True,
    )
    description = models.TextField(
        "توضیحات",
        blank=True,
        default="",
        null=True,
    )
    slug = models.SlugField(
        "اسلاگ",
        max_length=200,
        blank=True,
        unique=True,
    )
    is_active = models.BooleanField(
        "فعال/غیرفعال",
        default=False,
        blank=True,
    )
    created_at = models.DateTimeField(
        "تاریخ ایجاد",
        auto_now_add=True,
    )

    file_upload = FileUpload("images", "logo")

    logo = models.ImageField(
        "لوگو",
        upload_to=file_upload,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.store_name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.store_name) or "store"
            slug = base_slug
            counter = 1

            while Store.objects.filter(
                slug=slug
            ).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'فروشگاه'
        verbose_name_plural = 'فروشگاه‌ها'