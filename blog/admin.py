from django.contrib import admin
from .models import Review


@admin.action(description="Одобрить выбранные комментарии")
def approve_reviews(modeladmin, request, queryset):
    updated = queryset.update(status=Review.Status.APPROVED)
    modeladmin.message_user(request, f"{updated} комментариев одобрено")


@admin.action(description="Отклонить выбранные комментарии")
def reject_reviews(modeladmin, request, queryset):
    updated = queryset.update(status=Review.Status.REJECTED)
    modeladmin.message_user(request, f"{updated} комментариев отклонено")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["name", "post", "rating", "status", "is_admin", "created_at"]
    list_filter = ["status", "is_admin", "rating"]
    search_fields = ["name", "text", "post__title"]
    list_editable = ["status"]
    autocomplete_fields = ["parent"]
    readonly_fields = ["ip_address", "created_at"]
    actions = [approve_reviews, reject_reviews]