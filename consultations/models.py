from django.db import models
from django.core.validators import RegexValidator
from ckeditor.fields import RichTextField


class EmailTemplate(models.Model):
    """Модель для хранения email шаблонов"""
    name = models.CharField(max_length=100, verbose_name="Название шаблона")
    subject = models.CharField(max_length=200, verbose_name="Тема письма")
    html_content = RichTextField(
        config_name='email_template',
        verbose_name="HTML контент",
        help_text="Используйте переменные: {{ name }}, {{ phone }}, {{ problem }}, {{ created_at }}"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Email шаблон"
        verbose_name_plural = "Email шаблоны"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ConsultationRequest(models.Model):
    """Модель для хранения заявок на консультацию"""
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('processing', 'В обработке'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]

    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.CharField(
        max_length=20, 
        verbose_name="Телефон",
        validators=[
            RegexValidator(
                regex=r'^[\+]?[0-9\s\-\(\)]{10,}$',
                message='Введите корректный номер телефона'
            )
        ]
    )
    problem = models.TextField(verbose_name="Описание проблемы")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='new',
        verbose_name="Статус"
    )
    admin_notes = models.TextField(blank=True, verbose_name="Примечания администратора")
    email_sent_to_user = models.BooleanField(default=False, verbose_name="Email отправлен пользователю")
    email_sent_to_admin = models.BooleanField(default=False, verbose_name="Email отправлен администратору")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Заявка на консультацию"
        verbose_name_plural = "Заявки на консультацию"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"

    @property
    def short_problem(self):
        """Краткое описание проблемы для админки"""
        return self.problem[:100] + "..." if len(self.problem) > 100 else self.problem


class FormSettings(models.Model):
    """Настройки формы консультации"""
    title = models.CharField(max_length=200, default="Получить консультацию", verbose_name="Заголовок")
    subtitle = models.TextField(default="Заполните форму ниже, и наш эксперт свяжется с вами в течение 24 часов для предоставления бесплатной консультации.", verbose_name="Подзаголовок")
    
    # Тексты для модального окна
    modal_title = models.CharField(max_length=200, default="Потеряли деньги? Не знаете что делать?", verbose_name="Заголовок модального окна")
    modal_subtitle = models.CharField(max_length=200, default="Получите бесплатную консультацию!", verbose_name="Подзаголовок модального окна")
    
    # Настройки email
    admin_email = models.EmailField(verbose_name="Email администратора")
    user_email_template = models.ForeignKey(
        EmailTemplate, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='user_templates',
        verbose_name="Шаблон email для пользователя"
    )
    admin_email_template = models.ForeignKey(
        EmailTemplate, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='admin_templates',
        verbose_name="Шаблон email для администратора"
    )
    
    # Настройки отображения
    show_modal_after_seconds = models.IntegerField(default=3, verbose_name="Показать модальное окно через (секунд)")
    is_modal_enabled = models.BooleanField(default=True, verbose_name="Включить модальное окно")
    
    class Meta:
        verbose_name = "Настройки формы"
        verbose_name_plural = "Настройки формы"

    def __str__(self):
        return "Настройки формы консультации"

    def save(self, *args, **kwargs):
        # Обеспечиваем только один экземпляр настроек
        if not self.pk and FormSettings.objects.exists():
            return
        super().save(*args, **kwargs)
