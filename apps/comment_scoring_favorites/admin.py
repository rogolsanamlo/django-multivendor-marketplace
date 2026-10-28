from django.contrib import admin

from .models import Comment, Favorite, Scoring


@admin.action(description='تأیید نظرهای انتخاب شده')
def approve_comments(modeladmin, request, queryset):
    updated = queryset.update(
        is_active=True,
        approving_user=request.user,
    )

    modeladmin.message_user(request, f'{updated} نظر تأیید شد.')


@admin.action(description='عدم نمایش نظرهای انتخاب شده')
def hide_comments(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)

    modeladmin.message_user(request, f'{updated} نظر از نمایش خارج شد.')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'store_product',
        'commenting_user',
        'comment_text',
        'is_active',
        'register_date',
    )

    list_filter = (
        'is_active',
        'register_date',
    )

    search_fields = (
        'comment_text',
        'commenting_user__mobile_number',
        'commenting_user__family',
    )

    ordering = ('-register_date',)

    actions = (approve_comments, hide_comments)

    def save_model(self, request, obj, form, change):
        if obj.is_active and obj.approving_user is None:
            obj.approving_user = request.user

        super().save_model(request, obj, form, change)


@admin.register(Scoring)
class ScoringAdmin(admin.ModelAdmin):
    list_display = (
        'store_product',
        'scoring_user',
        'score',
        'register_date',
    )

    list_filter = ('score',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'store_product',
        'favorite_user',
        'register_date',
    )
