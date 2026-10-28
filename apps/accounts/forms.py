from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import CustomUser, UserProfile, Store
from .validators import (
    validate_phone,
    validate_password_strength,
    validate_passwords,
    validate_image,
)
from .services import (
    validate_exists_mobile_number,
    validate_unique_email,
)


class PasswordValidationMixin:

    def validate_password_fields(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        validate_passwords(
            password1,
            password2
        )

        validate_password_strength(password1)

        return password2


class UserCreationForm(PasswordValidationMixin, forms.ModelForm):

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )

    password2 = forms.CharField(
        label="RePassword",
        widget=forms.PasswordInput
    )

    class Meta:
        model = CustomUser
        fields = [
            'mobile_number',
            'email',
            'name',
            'family',
        ]

        error_messages = {
            'mobile_number': {
                'required': 'شماره موبایل الزامی است.',
                'unique': 'این شماره قبلا ثبت شده است'
            }
        }

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')

        validate_phone(mobile, 'mobile')

        return mobile

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email:
            validate_unique_email(email)

        return email

    def clean_password2(self):
        return self.validate_password_fields()

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')

        if password:
            user.set_password(password)

        if commit:
            user.save()

        return user


class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField(
        help_text="برای تغییر رمز عبور روی این <a href='../password'>لینک</a>"
    )

    class Meta:
        model = CustomUser
        fields = [
            'mobile_number',
            'password',
            'email',
            'name',
            'family',
            'is_active',
            'is_admin'
        ]


class RegisterUserForm(PasswordValidationMixin, forms.ModelForm):

    password1 = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'رمز را وارد کنید'
            }
        )
    )

    password2 = forms.CharField(
        label="تکرار رمز عبور",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'رمز را دوباره وارد کنید'
            }
        )
    )

    class Meta:
        model = CustomUser
        fields = [
            'mobile_number',
            'name',
            'family'
        ]

        widgets = {
            'mobile_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'موبایل را وارد کنید'
                }
            ),
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'نام'
                }
            ),
            'family': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'نام خانوادگی'
                }
            ),
        }

        error_messages = {
            'mobile_number': {
                'required': 'شماره موبایل الزامی است.',
                'unique': 'این شماره قبلا ثبت شده است'
            }
        }

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')

        validate_phone(mobile, 'mobile')

        return mobile

    def clean_password2(self):
        return self.validate_password_fields()

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')

        if password:
            user.set_password(password)

        if commit:
            user.save()

        return user


class VerifyRegisterForm(forms.Form):

    active_code = forms.CharField(
        label="کد فعال سازی",
        error_messages={
            "required": "این فیلد نمی تواند خالی باشد"
        },
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'کد دریافتی را وارد کنید'
            }
        )
    )


class LoginUserForm(forms.Form):

    mobile_number = forms.CharField(
        label="شماره موبایل",
        error_messages={
            "required": "این فیلد نمی تواند خالی باشد"
        },
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'موبایل را وارد کنید'
            }
        )
    )

    password = forms.CharField(
        label="رمز ورود",
        error_messages={
            "required": "این فیلد نمی تواند خالی باشد"
        },
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'رمز عبور را وارد کنید'
            }
        )
    )

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')

        validate_phone(mobile, 'mobile')

        return mobile


class ChangePasswordForm(PasswordValidationMixin, forms.Form):

    password1 = forms.CharField(
        label="رمز عبور",
        error_messages={
            "required": "این فیلد نمی تواند خالی باشد"
        },
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'رمز عبور را وارد کنید'
            }
        )
    )

    password2 = forms.CharField(
        label="تکرار رمز عبور",
        error_messages={
            "required": "این فیلد نمی تواند خالی باشد"
        },
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'تکرار رمز عبور را وارد کنید'
            }
        )
    )

    def clean_password2(self):
        return self.validate_password_fields()


class RememberPasswordForm(forms.Form):

    mobile_number = forms.CharField(
        label="شماره موبایل",
        error_messages={
            "required": "شماره موبایل الزامی است"
        },
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'موبایل را وارد کنید'
            }
        )
    )

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')

        validate_phone(mobile, 'mobile')
        validate_exists_mobile_number(mobile)

        return mobile


class ImageValidationMixin:

    def validate_uploaded_image(self, image):
        if image:
            validate_image(image)

        return image


class StoreFormWidgetMixin:

    store_widgets = {
        'store_name': forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'نام فروشگاه'
            }
        ),
        'store_phone': forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'شماره فروشگاه'
            }
        ),
        'address': forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'آدرس فروشگاه'
            }
        ),
        'description': forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'توضیحات فروشگاه'
            }
        ),
        'logo': forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        ),
    }


class CreateStoreForm(
    StoreFormWidgetMixin,
    ImageValidationMixin,
    forms.ModelForm
):

    class Meta:
        model = Store
        fields = [
            'store_name',
            'store_phone',
            'address',
            'description',
            'logo'
        ]

        error_messages = {
            'store_phone': {
                'required': 'شماره فروشگاه الزامی است.',
                'unique': 'این شماره قبلاً ثبت شده است.'
            }
        }

        widgets = StoreFormWidgetMixin.store_widgets

    def clean_store_phone(self):
        phone = self.cleaned_data.get('store_phone')

        validate_phone(phone, 'store')

        return phone

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')

        return self.validate_uploaded_image(logo)


class EditStoreForm(
    StoreFormWidgetMixin,
    ImageValidationMixin,
    forms.ModelForm
):

    class Meta:
        model = Store
        fields = [
            'store_name',
            'store_phone',
            'address',
            'description',
            'logo'
        ]

        error_messages = {
            'store_phone': {
                'required': 'شماره فروشگاه الزامی است.',
                'unique': 'این شماره قبلاً ثبت شده است.'
            }
        }

        widgets = StoreFormWidgetMixin.store_widgets

    def clean_store_phone(self):
        phone = self.cleaned_data.get('store_phone')

        validate_phone(phone, 'store')

        return phone

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')

        return self.validate_uploaded_image(logo)


class UpdateProfileForm(forms.ModelForm):

    class Meta:
        model = CustomUser

        fields = [
            'name',
            'family',
            'email'
        ]

        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'نام'
                }
            ),
            'family': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'نام خانوادگی'
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ایمیل'
                }
            ),
        }



    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email and CustomUser.objects.filter(
            email__iexact=email
        ).exclude(pk=self.instance.pk).exists():
            raise ValidationError(
                "این ایمیل قبلا ثبت شده است."
            )

        return email


class UpdateUserProfileForm(
    ImageValidationMixin,
    forms.ModelForm
):

    class Meta:
        model = UserProfile

        fields = [
            'address',
            'image_name'
        ]

        widgets = {
            'address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'آدرس'
                }
            ),
            'image_name': forms.FileInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }

    def clean_image_name(self):
        image = self.cleaned_data.get('image_name')

        return self.validate_uploaded_image(image)