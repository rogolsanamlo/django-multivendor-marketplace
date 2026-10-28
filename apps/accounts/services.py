from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


CustomUser = get_user_model()


def validate_exists_mobile_number(mobile):
    if not CustomUser.objects.filter(
        mobile_number=mobile
    ).exists():
        raise ValidationError(
            "این شماره موبایل قبلا ثبت نشده است."
        )


def validate_unique_email(email):
    if CustomUser.objects.filter(
        email__iexact=email
    ).exists():
        raise ValidationError(
            "این ایمیل قبلا ثبت شده است"
        )