from django.contrib import admin
from django.utils.html import format_html
from .models import HeroBanner, ContactInfo, Service, AboutUs, OurMission, OurTeam, OurValues


# @admin.register(SiteSection)
# class SiteSectionAdmin(admin.ModelAdmin):
#     list_display = ['name', 'title', 'is_active', 'order', 'updated_at']
#     list_filter = ['is_active', 'name']
#     search_fields = ['title', 'content']
#     list_editable = ['is_active', 'order']
#     readonly_fields = ['created_at', 'updated_at']
    
#     fieldsets = (
#         ('Основна інформація', {
#             'fields': ('name', 'title', 'subtitle', 'is_active', 'order')
#         }),
#         ('Контент', {
#             'fields': ('content',)
#         }),
#         ('Метадані', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'short_description', 'is_active', 'order', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'order']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'description', 'is_active', 'order')
        }),
        ('Іконка', {
            'fields': ('icon_svg',),
            'description': 'Вставте SVG код іконки'
        }),
        ('Метадані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def short_description(self, obj):
        """Короткий опис для списку"""
        return obj.description[:100] + "..." if len(obj.description) > 100 else obj.description
    short_description.short_description = "Опис"


# @admin.register(SiteSettings)
# class SiteSettingsAdmin(admin.ModelAdmin):
#     def has_add_permission(self, request):
#         # Дозволяємо створити тільки один екземпляр
#         return not SiteSettings.objects.exists()

#     def has_delete_permission(self, request, obj=None):
#         # Забороняємо видалення
#         return False

#     fieldsets = (
#         ('Основна інформація', {
#             'fields': ('site_name', 'site_description')
#         }),
#         ('Зображення', {
#             'fields': ('logo', 'favicon', 'og_image', 'twitter_image')
#         }),
#         ('SEO налаштування', {
#             'fields': ('meta_title', 'meta_description', 'meta_keywords')
#         }),
#         ('Контактна інформація', {
#             'fields': ('contact_email', 'contact_phone')
#         }),
#         ('Аналітика', {
#             'fields': ('google_analytics_id', 'yandex_metrika_id'),
#             'classes': ('collapse',)
#         }),
#     )

#     def get_readonly_fields(self, request, obj=None):
#         # Робимо всі поля тільки для читання після створення
#         if obj:
#             return [field.name for field in obj._meta.fields]
#         return []


@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'subtitle', 'is_active', 'order', 'preview_background', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'subtitle', 'description']
    list_editable = ['is_active', 'order']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'subtitle', 'description', 'is_active', 'order')
        }),
        ('Дизайн', {
            'fields': ('background_image', 'background_color'),
            'description': 'Налаштування зовнішнього вигляду банера'
        }),
        ('Кнопка', {
            'fields': ('button_text', 'button_url'),
            'description': 'Налаштування кнопки дії'
        }),
        ('Метадані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def preview_background(self, obj):
        """Попередній перегляд фону"""
        if obj.background_image:
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 30px; border-radius: 4px;" />',
                obj.background_image.url
            )
        elif obj.background_color:
            return format_html(
                '<div style="width: 50px; height: 30px; background-color: {}; border-radius: 4px; border: 1px solid #ddd;"></div>',
                obj.background_color
            )
        return "Немає фону"
    preview_background.short_description = "Фон"

@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ['email', 'phone', 'telegram']
    search_fields = ['email', 'phone', 'telegram']
    
    fieldsets = (   
        ('Основна інформація', {
            'fields': ('email', 'phone', 'telegram')
        }),
    )

@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    

@admin.register(OurMission)
class OurMissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(OurTeam)
class OurTeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'description']
    search_fields = ['name', 'position', 'description']

@admin.register(OurValues)
class OurValuesAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
    search_fields = ['title', 'description']