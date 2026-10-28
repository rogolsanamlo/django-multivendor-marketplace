from django import forms

from apps.products.models import Product, StoreProduct


class SellerStoreProductForm(forms.ModelForm):
    """A seller lists a catalog product in their own store with their own price."""

    class Meta:
        model = StoreProduct
        fields = ['product', 'price', 'is_active']
        labels = {
            'product': 'کالا',
            'price': 'قیمت (تومان)',
            'is_active': 'نمایش در فروشگاه',
        }
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 0, 'step': 1}
            ),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }
        error_messages = {
            'product': {
                'invalid_choice': 'این کالا قابل انتخاب نیست یا قبلاً به فروشگاه شما اضافه شده است.',
                'required': 'انتخاب کالا الزامی است.',
            },
            'price': {
                'required': 'قیمت الزامی است.',
            },
        }

    def __init__(self, *args, store=None, **kwargs):
        super().__init__(*args, **kwargs)

        products = Product.objects.filter(is_active=True)

        if self.instance.pk:
            # The product of an existing listing cannot be changed.
            self.fields['product'].disabled = True
            products = Product.objects.all()
        elif store is not None:
            products = products.exclude(store_products__store=store)

        self.fields['product'].queryset = products
        self.fields['product'].empty_label = 'یک کالا انتخاب کنید'

    def clean_price(self):
        price = self.cleaned_data.get('price')

        if price is None or price <= 0:
            raise forms.ValidationError('قیمت باید بیشتر از صفر باشد.')

        return price


class SellerStockForm(forms.Form):
    """Register stock coming into / leaving the store's warehouse."""

    MOVEMENT_CHOICES = [
        ('input', 'ورود به انبار'),
        ('output', 'خروج از انبار'),
    ]

    store_product = forms.ModelChoiceField(
        queryset=StoreProduct.objects.none(),
        label='کالا',
        empty_label='یک کالا انتخاب کنید',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    movement = forms.ChoiceField(
        choices=MOVEMENT_CHOICES,
        label='نوع تغییر موجودی',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    qty = forms.IntegerField(
        min_value=1,
        label='تعداد',
        error_messages={'min_value': 'تعداد باید حداقل ۱ باشد.'},
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
    )

    price = forms.IntegerField(
        min_value=0,
        required=False,
        label='قیمت خرید هر واحد (اختیاری)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
    )

    def __init__(self, *args, store, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['store_product'].queryset = (
            StoreProduct.objects
            .filter(store=store)
            .select_related('product')
        )

    def clean(self):
        cleaned = super().clean()

        store_product = cleaned.get('store_product')
        qty = cleaned.get('qty')

        if (
            cleaned.get('movement') == 'output'
            and store_product
            and qty
            and qty > store_product.get_number_in_warehouse()
        ):
            self.add_error('qty', 'تعداد خروجی بیشتر از موجودی انبار است.')

        return cleaned
