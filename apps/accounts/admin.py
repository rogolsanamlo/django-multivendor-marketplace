from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core import serializers
from django.http import HttpResponse

from .forms import UserChangeForm, UserCreationForm
from .models import CustomUser, Store, UserProfile


class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        'mobile_number',
        'email',
        'name',
        'family',
        'is_active',
        'is_admin',
    )

    list_filter = (
        'is_active',
        'is_admin',
        'family',
    )

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'mobile_number',
                    'password',
                )
            }
        ),
        (
            'اطلاعات شخصی',
            {
                'fields': (
                    'email',
                    'name',
                    'family',
                    'active_code',
                )
            }
        ),
        (
            'دسترسی‌ها',
            {
                'fields': (
                    'is_active',
                    'is_admin',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            }
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                'fields': (
                    'mobile_number',
                    'email',
                    'name',
                    'family',
                    'password1',
                    'password2',
                )
            }
        ),
    )

    search_fields = (
        'mobile_number',
        'name',
        'family',
        'email',
    )

    ordering = ('mobile_number',)


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'address',
    )


def deactivate_store(modeladmin, request, queryset):
    result = queryset.update(is_active=False)
    message = f'{result} فروشگاه غیرفعال شد.'
    modeladmin.message_user(request, message)


def activate_store(modeladmin, request, queryset):
    result = queryset.update(is_active=True)
    message = f'{result} فروشگاه فعال شد.'
    modeladmin.message_user(request, message)


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


deactivate_store.short_description = (
    'غیرفعال کردن فروشگاه‌های انتخاب شده'
)

activate_store.short_description = (
    'فعال کردن فروشگاه‌های انتخاب شده'
)

export_json.short_description = (
    'خروجی JSON از فروشگاه‌های انتخاب شده'
)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = (
        'store_name',
        'user',
        'store_phone',
        'is_active',
        'created_at',
    )

    list_filter = (
        'is_active',
        'created_at',
    )

    search_fields = (
        'store_name',
        'store_phone',
        'user__mobile_number',
    )

    list_editable = (
        'is_active',
    )

    ordering = (
        '-created_at',
    )

    actions = (
        activate_store,
        deactivate_store,
        export_json,
    )