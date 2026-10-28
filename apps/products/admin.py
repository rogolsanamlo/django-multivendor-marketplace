from django.contrib import admin
from django.core import serializers
from django.db.models import Count, Q
from django.http import HttpResponse
from django.contrib.admin import SimpleListFilter
from django_admin_listfilter_dropdown.filters import DropdownFilter

from utils import generate_unique_slug

from apps.products.models import (
    Brand,
    Feature,
    FeatureValue,
    Product,
    ProductFeature,
    ProductGallery,
    ProductGroup,
    StoreProduct,
)


SLUG_LABEL = 'اسلاگ (آدرس یکتا)'

SLUG_HELP = 'اختیاری؛ اگر خالی بماند به‌صورت خودکار ساخته می‌شود.'

HELP_TEXTS = {
    'group_parent': (
        'اگر خالی بماند، این یک «گروه اصلی» است. '
        'برای ساخت «زیرگروه»، گروه اصلی را اینجا انتخاب کنید.'
    ),
    'product_group': (
        'فقط زیرگروه‌ها نمایش داده می‌شوند. اگر لیست خالی است، '
        'ابتدا در بخش «گروه‌های کالا» یک زیرگروه بسازید.'
    ),
}


class PersianFormMixin:
    """
    Persian labels/help texts for the admin forms and an automatic slug.

    Set ``slug_source`` (the title field) and ``slug_prefix`` on the admin.
    """

    slug_source = None
    slug_prefix = 'item'

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)

        if field is None:
            return field

        if db_field.name == 'slug':
            field.label = SLUG_LABEL
            field.help_text = SLUG_HELP
            field.required = False

        if db_field.name in HELP_TEXTS:
            field.help_text = HELP_TEXTS[db_field.name]

        return field

    def fill_slug(self, obj):
        if self.slug_source and not obj.slug:
            obj.slug = generate_unique_slug(
                type(obj),
                getattr(obj, self.slug_source, ''),
                self.slug_prefix,
                obj,
            )

    def save_model(self, request, obj, form, change):
        self.fill_slug(obj)
        super().save_model(request, obj, form, change)


@admin.register(Brand)
class BrandAdmin(PersianFormMixin, admin.ModelAdmin):
    slug_source = 'brand_title'
    slug_prefix = 'brand'

    list_display = (
        'brand_title',
        'slug',
    )
    search_fields = (
        'brand_title',
    )
    ordering = (
        'brand_title',
    )


def de_active_product_group(modeladmin, request, queryset):
    result = queryset.update(is_active=False)

    message = (
        f'گروه تعداد {result} کالا غیر فعال شد'
    )

    modeladmin.message_user(
        request,
        message
    )


def active_product_group(modeladmin, request, queryset):
    result = queryset.update(is_active=True)

    message = (
        f'تعداد گروه {result} کالا فعال شد'
    )

    modeladmin.message_user(
        request,
        message
    )


def export_json(modeladmin, request, queryset):
    response = HttpResponse(
        content_type='application/json'
    )

    serializers.serialize(
        'json',
        queryset,
        stream=response
    )

    return response


class GroupFilter(SimpleListFilter):
    title = 'گروه محصولات'
    parameter_name = 'group'

    def lookups(self, request, model_admin):
        sub_groups = ProductGroup.objects.filter(
            group_parent__isnull=False
        )

        groups = set(
            item.group_parent
            for item in sub_groups
        )

        return [
            (item.id, item.group_title)
            for item in groups
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                Q(group_parent=self.value())
            )

        return queryset


class ProductGroupInstanceInlineAdmin(PersianFormMixin, admin.TabularInline):
    model = ProductGroup
    extra = 0
    verbose_name = 'زیرگروه'
    verbose_name_plural = 'زیرگروه‌ها'


@admin.register(ProductGroup)
class ProductGroupAdmin(PersianFormMixin, admin.ModelAdmin):
    slug_source = 'group_title'
    slug_prefix = 'group'

    list_display = (
        'is_active',
        'register_date',
        'group_title',
        'group_parent',
        'slug',
        'update_date',
        'count_product_of_group',
        'count_sub_group',
    )

    list_filter = (
        GroupFilter,
        ('group_parent', DropdownFilter),
        'is_active',
    )

    search_fields = (
        'group_title',
    )

    ordering = (
        'group_parent',
        'group_title',
    )

    inlines = [
        ProductGroupInstanceInlineAdmin,
    ]

    actions = [
        de_active_product_group,
        active_product_group,
        export_json,
    ]

    def save_formset(self, request, form, formset, change):
        # Sub-groups added inline also get an automatic slug.
        instances = formset.save(commit=False)

        for obj in formset.deleted_objects:
            obj.delete()

        for obj in instances:
            self.fill_slug(obj)
            obj.save()

        formset.save_m2m()

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        queryset = queryset.annotate(
            sub_group=Count('groups')
        )

        queryset = queryset.annotate(
            product_of_group=Count(
                'products_of_groups',
                distinct=True
            )
        )

        return queryset

    @admin.display(
        description='تعداد زیر گروه ها',
        ordering='sub_group'
    )
    def count_sub_group(self, obj):
        return obj.sub_group

    @admin.display(
        description='تعداد کالاهای گروه',
        ordering='product_of_group'
    )
    def count_product_of_group(self, obj):
        return obj.product_of_group


de_active_product_group.short_description = (
    'غیر فعال کردن گروه های انتخاب شده'
)

active_product_group.short_description = (
    'فعال کردن گروه های انتخاب شده'
)

export_json.short_description = (
    'خروجی JSON از گروه های انتخاب شده'
)


class FeatureValueInline(admin.TabularInline):
    model = FeatureValue
    extra = 3


@admin.register(Feature)
class FeatureAdmin(PersianFormMixin, admin.ModelAdmin):
    list_display = (
        'feature_name',
        'display_groups',
        'display_feature_values',
    )

    list_filter = (
        'feature_name',
    )

    search_fields = (
        'feature_name',
    )

    ordering = (
        'feature_name',
    )

    inlines = [
        FeatureValueInline,
    ]

    def formfield_for_manytomany(
        self,
        db_field,
        request,
        **kwargs
    ):
        if db_field.name == 'product_group':
            queryset = ProductGroup.objects.filter(
                group_parent__isnull=False
            )

            kwargs['queryset'] = queryset

        return super().formfield_for_manytomany(
            db_field,
            request,
            **kwargs
        )

    @admin.display(
        description='گروه های دارای این ویژگی'
    )
    def display_groups(self, obj):
        groups = obj.product_group.all()

        return ', '.join(
            group.group_title
            for group in groups
        )

    @admin.display(
        description='مقادیر ممکن برای این ویژگی'
    )
    def display_feature_values(self, obj):
        feature_values = obj.feature_values.all()

        return ', '.join(
            feature_value.value_title
            for feature_value in feature_values
        )


def de_active_product(modeladmin, request, queryset):
    result = queryset.update(is_active=False)

    message = (
        f'تعداد {result} کالا غیر فعال شد'
    )

    modeladmin.message_user(
        request,
        message
    )


def active_product(modeladmin, request, queryset):
    result = queryset.update(is_active=True)

    message = (
        f'تعداد {result} کالا فعال شد'
    )

    modeladmin.message_user(
        request,
        message
    )


class ProductFeatureInLine(admin.TabularInline):
    model = ProductFeature
    extra = 5

    class Media:
        css = {
            'all': (
                'css/admin_style.css',
            )
        }

        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
            'js/admin_script.js',
        )


class ProductProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 3


@admin.register(Product)
class ProductAdmin(PersianFormMixin, admin.ModelAdmin):
    slug_source = 'product_name'
    slug_prefix = 'product'

    list_display = (
        'product_name',
        'brand',
        'is_active',
        'slug',
        'display_product_groups',
        'update_date',
    )

    list_filter = (
        ('brand__brand_title', DropdownFilter),
        ('product_group__group_title', DropdownFilter),
    )

    search_fields = (
        'product_name',
    )

    ordering = (
        'update_date',
        'product_name',
    )

    actions = [
        de_active_product,
        active_product,
    ]

    inlines = [
        ProductFeatureInLine,
        ProductProductGalleryInline,
    ]

    fieldsets = (
        (
            'اطلاعات محصول',
            {
                'fields': (
                    'product_name',
                    'image_name',
                    (
                        'product_group',
                        'brand',
                        'is_active',
                    ),
                    'description',
                    'slug',
                )
            }
        ),
    )

    @admin.display(
        description='گروه های کالا'
    )
    def display_product_groups(self, obj):
        groups = obj.product_group.all()

        return ', '.join(
            group.group_title
            for group in groups
        )

    def formfield_for_manytomany(
        self,
        db_field,
        request,
        **kwargs
    ):
        if db_field.name == 'product_group':
            queryset = ProductGroup.objects.filter(
                group_parent__isnull=False
            )

            kwargs['queryset'] = queryset

        return super().formfield_for_manytomany(
            db_field,
            request,
            **kwargs
        )


@admin.register(StoreProduct)
class StoreProductAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'store',
        'price',
        'is_active',
        'register_date',
    )

    list_filter = (
        'is_active',
        'store',
    )

    search_fields = (
        'product__product_name',
        'store__store_name',
    )

    ordering = (
        '-register_date',
    )

    autocomplete_fields = (
        'product',
        'store',
    )

    actions = [
        de_active_product,
        active_product,
    ]