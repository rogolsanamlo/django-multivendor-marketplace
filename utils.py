import os
import random
from uuid import uuid4

from django.conf import settings
from django.utils.deconstruct import deconstructible
from django.utils.text import slugify
from kavenegar import APIException, HTTPException, KavenegarAPI


@deconstructible
class FileUpload:
    """
    Builds dynamic upload paths: <dir>/<prefix>/<uuid><ext>.

    The class is deconstructible and callable so Django can serialize it in
    migrations. Using a bound method as ``upload_to`` makes ``makemigrations``
    detect a "new" change on every run.

    کلاس کمکی برای ساخت مسیر آپلود فایل‌ها؛ منطق مسیردهی در یک جا متمرکز
    می‌شود و با تغییر storage (مثلاً S3) نیازی به تغییر مدل‌ها نیست.
    """

    def __init__(self, dir, prefix):
        self.dir = dir
        self.prefix = prefix

    def __call__(self, instance, filename):
        _, ext = os.path.splitext(filename)
        return f"{self.dir}/{self.prefix}/{uuid4()}{ext}"

    # Kept so older migrations referencing ``FileUpload.upload_to`` still load.
    def upload_to(self, instance, filename):
        return self(instance, filename)


def create_random_code(count):
    count -= 1
    return random.randint(10**count, 10**(count + 1) - 1)


def price_by_delivery_tax(price, discount=0):
    delivery = 2500
    if price > 500000:
        delivery = 0

    tax = (price + delivery) * 0.09
    total = price + delivery + tax
    total = total - (total * (discount or 0) / 100)
    return int(total), delivery, int(tax)


def send_sms(mobile_number, message):
    api_key = getattr(settings, "KAVENEGAR_API_KEY", "")

    if not api_key:
        # Development fallback: no SMS provider configured.
        print(f"[SMS disabled] to {mobile_number}: {message}")
        return None

    try:
        api = KavenegarAPI(api_key)
        params = {
            "sender": "",
            "receptor": mobile_number,
            "message": message,
        }
        return api.sms_send(params)

    except APIException as error:
        print(f"error1:{error}")
    except HTTPException as error:
        print(f"error2:{error}")


def generate_unique_slug(model, text, fallback_prefix, instance=None):
    """
    Build a unique slug for ``model``.

    Persian titles cannot be turned into an ASCII slug, so in that case a short
    random suffix is used: ``<fallback_prefix>-<8 hex chars>``.
    """
    base = slugify(text or '')

    if not base:
        base = f"{fallback_prefix}-{uuid4().hex[:8]}"

    queryset = model.objects.all()

    if instance is not None and instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    slug = base
    counter = 1

    while queryset.filter(slug=slug).exists():
        counter += 1
        slug = f"{base}-{counter}"

    return slug
