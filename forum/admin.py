from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    ForumCategory, ForumTopic, ForumPost, 
    ForumModerationLog, ForumNotification
)


@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'order', 'is_active', 'topics_count', 'posts_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description', 'icon', 'order', 'is_active')
        }),
        ('SEO настройки', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def topics_count(self, obj):
        return obj.get_topics_count()
    topics_count.short_description = "Тем"
    
    def posts_count(self, obj):
        return obj.get_posts_count()
    posts_count.short_description = "Постов"


@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'status', 'is_active', 'views_count', 'posts_count', 'created_at']
    list_filter = ['category', 'status', 'is_active', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'content', 'category', 'author', 'status', 'is_active')
        }),
        ('SEO настройки', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def posts_count(self, obj):
        return obj.get_posts_count()
    posts_count.short_description = "Постов"


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'topic', 'get_author_display', 'parent', 'is_approved', 'is_moderated', 'replies_count', 'created_at']
    list_filter = ['is_approved', 'is_moderated', 'topic__category', 'created_at']
    search_fields = ['content', 'anonymous_name', 'anonymous_email', 'topic__title']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_posts', 'reject_posts', 'mark_as_moderated']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('topic', 'author', 'anonymous_name', 'anonymous_email', 'parent', 'content')
        }),
        ('Модерация', {
            'fields': ('is_approved', 'is_moderated'),
            'classes': ('collapse',)
        }),
        ('SEO настройки', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'og_title', 'og_description', 'og_image', 'canonical_url'),
            'classes': ('collapse',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_author_display(self, obj):
        if obj.author:
            return f"{obj.author.username} (зарегистрированный)"
        else:
            return f"{obj.anonymous_name} (анонимно)"
    get_author_display.short_description = "Автор"
    
    def replies_count(self, obj):
        return obj.get_replies_count()
    replies_count.short_description = "Ответов"
    
    def approve_posts(self, request, queryset):
        updated = queryset.update(is_approved=True, is_moderated=True)
        self.message_user(request, f'Одобрено {updated} постов.')
    approve_posts.short_description = "Одобрить выбранные посты"
    
    def reject_posts(self, request, queryset):
        updated = queryset.update(is_approved=False, is_moderated=True)
        self.message_user(request, f'Отклонено {updated} постов.')
    reject_posts.short_description = "Отклонить выбранные посты"
    
    def mark_as_moderated(self, request, queryset):
        updated = queryset.update(is_moderated=True)
        self.message_user(request, f'Помечено как промодерированные {updated} постов.')
    mark_as_moderated.short_description = "Пометить как промодерированные"


@admin.register(ForumModerationLog)
class ForumModerationLogAdmin(admin.ModelAdmin):
    list_display = ['moderator', 'post', 'action', 'reason', 'created_at']
    list_filter = ['action', 'created_at', 'moderator']
    search_fields = ['moderator__username', 'post__content', 'reason']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(ForumNotification)
class ForumNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'post', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'post__content']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'Помечено как прочитанные {updated} уведомления.')
    mark_as_read.short_description = "Пометить как прочитанные"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'Помечено как непрочитанные {updated} уведомления.')
    mark_as_unread.short_description = "Пометить как непрочитанные"
