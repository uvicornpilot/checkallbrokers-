from django.db import models
from ckeditor.fields import RichTextField


class HeroBanner(models.Model):
    """Модель для главного банера с формой"""
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    subtitle = models.CharField(max_length=500, blank=True, verbose_name="Подзаголовок")
    description = models.TextField(blank=True, verbose_name="Описание")
    background_image = models.ImageField(upload_to='hero/', blank=True, verbose_name="Фоновое изображение")
    background_color = models.CharField(max_length=7, default="#16C646", verbose_name="Цвет фона")
    button_text = models.CharField(max_length=100, default="Получить консультацию", verbose_name="Текст кнопки")
    button_url = models.CharField(max_length=200, blank=True, verbose_name="Ссылка кнопки")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Главный банер"
        verbose_name_plural = "Главные банеры"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Обеспечиваем только один активный банер
        if self.is_active:
            HeroBanner.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class SiteSection(models.Model):
    """Модель для различных секций сайта"""
    SECTION_CHOICES = [
        ('header', 'Хедер'),
        ('about', 'О проекте'),
        ('services', 'Услуги'),
        ('broker_banner', 'Банер подбора брокера'),
        ('contact_info', 'Информация для контактов'),
        ('footer', 'Футер'),
    ]
    
    name = models.CharField(max_length=100, choices=SECTION_CHOICES, unique=True, verbose_name="Название секции")
    title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок")
    subtitle = models.CharField(max_length=500, blank=True, verbose_name="Подзаголовок")
    content = RichTextField(blank=True, verbose_name="Контент")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Секция сайта"
        verbose_name_plural = "Секции сайта"
        ordering = ['order', 'name']

    def __str__(self):
        return self.get_name_display()


class Service(models.Model):
    """Модель для услуг"""
    title = models.CharField(max_length=200, verbose_name="Название услуги")
    description = models.TextField(verbose_name="Описание")
    icon_svg = models.TextField(blank=True, verbose_name="SVG иконка")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class SiteSettings(models.Model):
    """Общие настройки сайта"""
    site_name = models.CharField(max_length=100, default="Broker Control", verbose_name="Название сайта")
    site_description = models.CharField(max_length=500, default="Независимый информационно-аналитический проект по проверке брокеров", verbose_name="Описание сайта")
    logo = models.ImageField(upload_to='site/', blank=True, verbose_name="Логотип")
    favicon = models.ImageField(upload_to='site/', blank=True, verbose_name="Favicon")
    
    # SEO настройки
    meta_title = models.CharField(max_length=60, default="Broker Control - Анализ и оценка брокерских компаний", verbose_name="Meta Title")
    meta_description = models.CharField(max_length=160, default="Независимый информационно-аналитический проект по проверке брокеров и предоставлению юридических консультаций", verbose_name="Meta Description")
    meta_keywords = models.CharField(max_length=500, blank=True, verbose_name="Meta Keywords")
    
    # Социальные сети
    og_image = models.ImageField(upload_to='site/', blank=True, verbose_name="Open Graph изображение")
    twitter_image = models.ImageField(upload_to='site/', blank=True, verbose_name="Twitter изображение")
    
    # Контактная информация
    contact_email = models.EmailField(blank=True, verbose_name="Email для контактов")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон для контактов")
    
    # Аналитика
    google_analytics_id = models.CharField(max_length=50, blank=True, verbose_name="Google Analytics ID")
    yandex_metrika_id = models.CharField(max_length=50, blank=True, verbose_name="Yandex Metrika ID")
    
    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Настройки сайта"

    def save(self, *args, **kwargs):
        # Обеспечиваем только один экземпляр настроек
        if not self.pk and SiteSettings.objects.exists():
            return
        super().save(*args, **kwargs)


class ContactInfo(models.Model):
    """Общие настройки сайта"""
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    telegram = models.CharField(max_length=20, blank=True, verbose_name="Telegram")
    
    class Meta:
        verbose_name = "Контактная информация"
        verbose_name_plural = "Контактная информация"

    def __str__(self):
        return "Настройки сайта"


class AboutUs(models.Model):
    """О нас"""
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    
    class Meta:
        verbose_name = "О нас"
        verbose_name_plural = "О нас"

    def __str__(self):
        return self.title
    
class OurMission(models.Model):
    """Наша миссия"""
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    icon_svg = models.TextField(blank=True, verbose_name="SVG иконка")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    
    class Meta:
        verbose_name = "Наша миссия"
        verbose_name_plural = "Наша миссия"

class OurTeam(models.Model):
    """Наша команда"""
    name = models.CharField(max_length=200, verbose_name="Имя")
    position = models.CharField(max_length=200, verbose_name="Должность")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(upload_to='our_team/', blank=True, verbose_name="Изображение")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    
    class Meta:
        verbose_name = "Наша команда"
        verbose_name_plural = "Наша команда"

    def __str__(self):
        return self.name

class OurValues(models.Model):
    """Наши преимущества"""
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    
    
    class Meta:
        verbose_name = "Наши преимущества"
        verbose_name_plural = "Наши преимущества"

    def __str__(self):
        return self.title
    