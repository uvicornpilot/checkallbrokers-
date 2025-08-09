from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Tag, Post, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'order', 'posts_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'order']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

    def posts_count(self, obj):
        """Кількість статей в категорії"""
        return obj.posts.count()
    posts_count.short_description = "Кількість статей"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'posts_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']

    def posts_count(self, obj):
        """Кількість статей з тегом"""
        return obj.posts.count()
    posts_count.short_description = "Кількість статей"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'category', 
        'status', 
        'published_at', 
        'views_count', 
        'reading_time_display',
        'created_at'
    ]
    list_filter = ['status', 'category', 'tags', 'published_at', 'created_at']
    search_fields = ['title', 'excerpt', 'content']
    list_editable = ['status']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    filter_horizontal = ['tags']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'author')
        }),
        ('Зображення', {
            'fields': ('featured_image',)
        }),
        ('Категорії та теги', {
            'fields': ('category', 'tags')
        }),
        ('Публікація', {
            'fields': ('status', 'published_at')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('views_count',),
            'classes': ('collapse',)
        }),
        ('Метадані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def reading_time_display(self, obj):
        """Відображення часу читання"""
        return f"{obj.reading_time} хв"
    reading_time_display.short_description = "Час читання"

    def get_queryset(self, request):
        """Оптимізація запитів"""
        return super().get_queryset(request).select_related('category').prefetch_related('tags')

    def save_model(self, request, obj, form, change):
        """Автоматичне встановлення дати публікації"""
        if obj.status == 'published' and not obj.published_at:
            from django.utils import timezone
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)

    actions = ['publish_posts', 'unpublish_posts']

    def publish_posts(self, request, queryset):
        """Опублікувати вибрані статті"""
        from django.utils import timezone
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} статей опубліковано')
    publish_posts.short_description = "Опублікувати вибрані статті"

    def unpublish_posts(self, request, queryset):
        """Зняти з публікації вибрані статті"""
        updated = queryset.update(status='draft', published_at=None)
        self.message_user(request, f'{updated} статей знято з публікації')
    unpublish_posts.short_description = "Зняти з публікації вибрані статті"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'post', 'rating', 'created_at', 'is_approved', 'is_admin', 'parent', 'avatar', 'ip_address']
    list_filter = ['is_approved', 'is_admin', 'rating', 'created_at']
    search_fields = ['name', 'text', 'post__title', 'avatar']
    readonly_fields = ['ip_address', 'created_at']
    list_editable = ['is_approved', 'is_admin']
    autocomplete_fields = ['post', 'parent']
    fieldsets = (
        (None, {
            'fields': ('post', 'parent', 'name', 'avatar', 'is_admin', 'rating', 'text', 'is_approved')
        }),
        ('Системные', {
            'fields': ('ip_address', 'created_at'),
            'classes': ('collapse',)
        })
    )
    actions = ['approve_reviews', 'reject_reviews']
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} отзывов было одобрено.')
    approve_reviews.short_description = "Одобрить выбранные отзывы"
    
    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} отзывов было отклонено.')
    reject_reviews.short_description = "Отклонить выбранные отзывы"
