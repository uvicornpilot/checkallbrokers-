from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import ConsultationRequest, EmailTemplate, FormSettings


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'subject']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'subject', 'is_active')
        }),
        ('Контент', {
            'fields': ('html_content',),
            'description': 'Використовуйте змінні: {{ name }}, {{ phone }}, {{ problem }}, {{ created_at }}'
        }),
        ('Метадані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'phone', 
        'short_problem_display', 
        'status', 
        'email_status',
        'created_at'
    ]
    list_filter = ['status', 'created_at', 'email_sent_to_user', 'email_sent_to_admin']
    search_fields = ['name', 'phone', 'problem']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['mark_as_processing', 'mark_as_completed', 'mark_as_cancelled', 'resend_emails']
    
    fieldsets = (
        ('Інформація про клієнта', {
            'fields': ('name', 'phone', 'problem')
        }),
        ('Статус та обробка', {
            'fields': ('status', 'admin_notes')
        }),
        ('Email статус', {
            'fields': ('email_sent_to_user', 'email_sent_to_admin'),
            'classes': ('collapse',)
        }),
        ('Метадані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def short_problem_display(self, obj):
        """Короткий опис проблеми в списку"""
        return obj.short_problem
    short_problem_display.short_description = "Проблема"

    def email_status(self, obj):
        """Статус відправки email"""
        user_status = "✅" if obj.email_sent_to_user else "❌"
        admin_status = "✅" if obj.email_sent_to_admin else "❌"
        return format_html(
            '<span title="Користувач: {} | Адмін: {}">👤{} 👨‍💼{}</span>',
            "Відправлено" if obj.email_sent_to_user else "Не відправлено",
            "Відправлено" if obj.email_sent_to_admin else "Не відправлено",
            user_status,
            admin_status
        )
    email_status.short_description = "Email статус"

    def mark_as_processing(self, request, queryset):
        """Позначити як 'В обробці'"""
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} заявок позначено як "В обробці"')
    mark_as_processing.short_description = "Позначити як 'В обробці'"

    def mark_as_completed(self, request, queryset):
        """Позначити як 'Завершена'"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} заявок позначено як "Завершена"')
    mark_as_completed.short_description = "Позначити як 'Завершена'"

    def mark_as_cancelled(self, request, queryset):
        """Позначити як 'Скасована'"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} заявок позначено як "Скасована"')
    mark_as_cancelled.short_description = "Позначити як 'Скасована'"

    def resend_emails(self, request, queryset):
        """Повторно відправити email"""
        # Тут буде логіка повторної відправки email
        self.message_user(request, f'Email буде відправлено для {queryset.count()} заявок')
    resend_emails.short_description = "Повторно відправити email"


@admin.register(FormSettings)
class FormSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Дозволяємо створити тільки один екземпляр
        return not FormSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Забороняємо видалення
        return False

    fieldsets = (
        ('Основні налаштування', {
            'fields': ('title', 'subtitle')
        }),
        ('Модальне вікно', {
            'fields': ('modal_title', 'modal_subtitle', 'show_modal_after_seconds', 'is_modal_enabled')
        }),
        ('Email налаштування', {
            'fields': ('admin_email', 'user_email_template', 'admin_email_template')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        # Робимо всі поля тільки для читання після створення
        if obj:
            return [field.name for field in obj._meta.fields]
        return []
