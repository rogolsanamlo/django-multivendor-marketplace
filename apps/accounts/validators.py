import os
import re

from django.core.exceptions import ValidationError
from PIL import Image


MAX_IMAGE_SIZE = 1024 * 1024


def validate_password_strength(password):
    if len(password) < 8:
        raise ValidationError("حداقل 8 کاراکتر باشد.")

    if not re.search(r'\d', password):
        raise ValidationError("حداقل شامل یک عدد باشد.")

    if not re.search(r'[A-Z]', password):
        raise ValidationError("حداقل شامل یک حرف بزرگ باشد.")

    if not re.search(r'[!@#$%^&*]', password):
        raise ValidationError("حداقل شامل یک کاراکتر خاص باشد.")

    if not re.fullmatch(
        r'^[a-zA-Z0-9!@#$%^&*]+$',
        password
    ):
        raise ValidationError(
            "کاراکتر غیرمجاز در رمز عبور وجود دارد."
        )


def validate_phone(phone, phone_type):
    if phone_type == 'mobile':
        pattern = r'^09\d{9}$'
    elif phone_type == 'store':
        pattern = r'^0\d{10}$'
    else:
        raise ValidationError("نوع شماره تلفن معتبر نیست.")

    if not re.match(pattern, phone):
        raise ValidationError("شماره تلفن معتبر نیست.")


def validate_passwords(password1, password2):
    if not password1:
        raise ValidationError("رمز عبور الزامی است.")

    if not password2:
        raise ValidationError("تکرار رمز عبور الزامی است.")

    if password1 != password2:
        raise ValidationError(
            "رمز عبور و تکرار با هم مغایرت دارد."
        )


def validate_image(image):
    if not image:
        return image

    ext = os.path.splitext(image.name)[1].lower()

    allowed_extensions = [
        '.jpg',
        '.jpeg',
        '.png',
        '.webp'
    ]

    if ext not in allowed_extensions:
        raise ValidationError(
            'فرمت فایل معتبر نیست'
        )

    if image.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            "سایز بزرگ است"
        )

    try:
        img = Image.open(image)
        img.verify()
    except Exception:
        raise ValidationError(
            "فایل تصویر معتبر نیست"
        )

    return image