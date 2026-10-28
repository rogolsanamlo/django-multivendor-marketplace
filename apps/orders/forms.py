from django import forms

from .models import PaymentType


class OrderForm(forms.Form):

    name = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "نام",
            }
        ),
        error_messages={
            "required": "این فیلد نمی تواند خالی باشد",
        },
    )

    family = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "نام خانوادگی",
            }
        ),
        error_messages={
            "required": "این فیلد نمی تواند خالی باشد",
        },
    )

    email = forms.EmailField(
        label="",
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "ایمیل",
            }
        ),
    )

    phone_number = forms.CharField(
        label="",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "شماره موبایل",
            }
        ),
    )

    address = forms.CharField(
        label="",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "آدرس",
                "rows": "2",
            }
        ),
        error_messages={
            "required": "این فیلد نمی تواند خالی باشد",
        },
    )

    description = forms.CharField(
        label="",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "توضیحات",
                "rows": "4",
            }
        ),
    )

    payment_type = forms.ModelChoiceField(
        queryset=PaymentType.objects.none(),
        empty_label=None,
        widget=forms.RadioSelect(attrs={"form": "checkout-form"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["payment_type"].queryset = (
            PaymentType.objects.all()
        )