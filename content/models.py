from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.contrib.settings.models import BaseGenericSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.models import Page, Orderable
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet
from wagtail.fields import RichTextField

from .auto_slug_mixin import AutoSlugPage  # поправьте путь под реальное расположение файла


# ──────────────────────────────────────────────────────────────────
#  Настройки сайта
# ──────────────────────────────────────────────────────────────────

@register_setting
class SiteSettings(BaseGenericSetting):
    """Общие настройки сайта — одна запись, редактируется в Settings → Site settings."""
    site_name = models.CharField(max_length=100, default="Broker Control")
    site_description = models.CharField(max_length=500, default="Независимый информационно-аналитический проект по проверке брокеров")
    logo = models.ImageField(upload_to='site/', blank=True)
    favicon = models.ImageField(upload_to='site/', blank=True)

    meta_title = models.CharField(max_length=60, default="Broker Control - Анализ и оценка брокерских компаний")
    meta_description = models.CharField(max_length=160, default="Независимый информационно-аналитический проект по проверке брокеров и предоставлению юридических консультаций")

    og_image = models.ImageField(upload_to='site/', blank=True)
    twitter_image = models.ImageField(upload_to='site/', blank=True)

    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_telegram = models.CharField(max_length=20, blank=True)  # заменяет ContactInfo

    company_registration_number = models.CharField(
        max_length=20, blank=True,
        verbose_name="Регистрационный номер компании (Companies House)",
        help_text="Например: 12345678",
    )

    google_analytics_id = models.CharField(max_length=50, blank=True)
    yandex_metrika_id = models.CharField(max_length=50, blank=True)

    panels = [
        MultiFieldPanel(
            [FieldPanel("site_name"), FieldPanel("site_description"), FieldPanel("logo"), FieldPanel("favicon")],
            heading="Основное",
        ),
        MultiFieldPanel(
            [FieldPanel("meta_title"), FieldPanel("meta_description")],
            heading="SEO по умолчанию",
        ),
        MultiFieldPanel(
            [FieldPanel("og_image"), FieldPanel("twitter_image")],
            heading="Соцсети",
        ),
        MultiFieldPanel(
            [FieldPanel("contact_email"), FieldPanel("contact_phone"), FieldPanel("contact_telegram"), FieldPanel("company_registration_number")],
            heading="Контакты",
        ),
        MultiFieldPanel(
            [FieldPanel("google_analytics_id"), FieldPanel("yandex_metrika_id")],
            heading="Аналитика",
        ),
    ]

    class Meta:
        verbose_name = "Настройки сайта"


# ──────────────────────────────────────────────────────────────────
#  Снипеты главной страницы
# ──────────────────────────────────────────────────────────────────

@register_snippet
class HeroBanner(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    background_image = models.ImageField(upload_to='hero/', blank=True)
    background_color = models.CharField(max_length=7, default="#16C646")
    button_text = models.CharField(max_length=100, default="Получить консультацию")
    button_url = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    panels = [
        FieldPanel("title"),
        FieldPanel("subtitle"),
        FieldPanel("description"),
        FieldPanel("background_image"),
        FieldPanel("background_color"),
        FieldPanel("button_text"),
        FieldPanel("button_url"),
        FieldPanel("is_active"),
        FieldPanel("order"),
    ]

    class Meta:
        verbose_name = "Главный баннер"
        ordering = ["order", "-pk"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.is_active:
            HeroBanner.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


@register_snippet
class SiteSection(models.Model):
    SECTION_CHOICES = [
        ('header', 'Хедер'),
        ('services', 'Услуги'),
        ('broker_banner', 'Баннер подбора брокера'),
        ('footer', 'Футер'),
    ]  # 'about' и 'contact_info' убраны — дублировали AboutUs/SiteSettings

    name = models.CharField(max_length=100, choices=SECTION_CHOICES, unique=True)
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=500, blank=True)
    content = RichTextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("title"),
        FieldPanel("subtitle"),
        FieldPanel("content"),
        FieldPanel("is_active"),
        FieldPanel("order"),
    ]

    class Meta:
        verbose_name = "Секция сайта"
        ordering = ["order", "name"]

    def __str__(self):
        return self.get_name_display()


class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon_svg = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("icon_svg"),
        FieldPanel("order"),
        FieldPanel("is_active"),
    ]

    class Meta:
        verbose_name = "Услуга"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title


# ──────────────────────────────────────────────────────────────────
#  СТАРЫЕ снипеты «О нас» — оставлены пока для обратной совместимости
#  (данные ещё в базе). Удалить отдельной миграцией ПОСЛЕ того, как
#  контент вручную перенесён в новую AboutPage ниже.
# ──────────────────────────────────────────────────────────────────

@register_snippet
class AboutUs(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    panels = [FieldPanel("title"), FieldPanel("description")]

    class Meta:
        verbose_name = "О нас (устарело)"
        verbose_name_plural = "О нас (устарело)"

    def __str__(self):
        return self.title


@register_snippet
class OurMission(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon_svg = models.TextField(blank=True)

    panels = [FieldPanel("title"), FieldPanel("description"), FieldPanel("icon_svg")]

    class Meta:
        verbose_name = "Наша миссия (устарело)"
        verbose_name_plural = "Наша миссия (устарело)"

    def __str__(self):
        return self.title


@register_snippet
class OurTeam(models.Model):
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='our_team/', blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("position"),
        FieldPanel("description"),
        FieldPanel("image"),
        FieldPanel("is_active"),
        FieldPanel("order"),
    ]

    class Meta:
        verbose_name = "Команда (устарело)"
        ordering = ["order"]

    def __str__(self):
        return self.name


@register_snippet
class OurValues(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    panels = [FieldPanel("title"), FieldPanel("description")]

    class Meta:
        verbose_name = "Наши преимущества (устарело)"
        verbose_name_plural = "Наши преимущества (устарело)"

    def __str__(self):
        return self.title


# ──────────────────────────────────────────────────────────────────
#  НОВЫЕ Wagtail-страницы (Pages) — About / Editorial Policy / Contacts
#  Все шаблоны лежат в корне проекта: templates/legal/
#  Наследуются от AutoSlugPage — slug генерируется автоматически
#  через slugify_ru (транслитерация), как у блога.
# ──────────────────────────────────────────────────────────────────

class AboutPage(AutoSlugPage):
    """
    Страница «О нас». Заменяет старые AboutUs / OurMission / OurTeam /
    OurValues — весь контент редактируется на одной странице в Wagtail:
    вводный текст, миссия, и два повторяющихся блока (команда, ценности)
    через InlinePanel.
    """
    template = "legal/about_page.html"

    intro = RichTextField(blank=True, verbose_name="Вводный текст")
    mission = RichTextField(blank=True, verbose_name="Наша миссия")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("mission"),
        InlinePanel("team_members", label="Команда"),
        InlinePanel("values", label="Ценности"),
    ]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = []

    class Meta:
        verbose_name = "Страница «О нас»"


class AboutPageTeamMember(Orderable):
    page = ParentalKey(
        AboutPage, on_delete=models.CASCADE, related_name="team_members"
    )
    name = models.CharField(max_length=120, verbose_name="Имя")
    role = models.CharField(max_length=120, blank=True, verbose_name="Должность")
    photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Фото",
    )
    bio = models.TextField(blank=True, verbose_name="Краткое описание")

    panels = [
        FieldPanel("name"),
        FieldPanel("role"),
        FieldPanel("photo"),
        FieldPanel("bio"),
    ]


class AboutPageValue(Orderable):
    page = ParentalKey(
        AboutPage, on_delete=models.CASCADE, related_name="values"
    )
    title = models.CharField(max_length=120, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
    ]


class EditorialPolicyPage(AutoSlugPage):
    """
    Страница «Редакционная политика». Один блок текста —
    как объясняется методология проверки брокеров, кто пишет обзоры,
    как отбираются источники. Важно для E-E-A-T сигналов Google.
    """
    template = "legal/editorial_policy_page.html"

    body = RichTextField(verbose_name="Текст политики")

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = []

    class Meta:
        verbose_name = "Страница «Редакционная политика»"


class ContactsPage(AutoSlugPage):
    """
    Страница «Контакты». Email / телефон / Telegram берутся из
    SiteSettings (те же данные, что в header/footer) — здесь
    редактируется только вводный текст и доп. реквизиты
    (адрес, часы работы).
    """
    template = "legal/contacts_page.html"

    intro = RichTextField(
        blank=True,
        verbose_name="Вводный текст",
        help_text="Короткое описание над контактными данными",
    )
    office_address = models.CharField(
        max_length=255, blank=True, verbose_name="Адрес офиса"
    )
    working_hours = models.CharField(
        max_length=255, blank=True,
        verbose_name="Часы работы",
        help_text="Например: Пн–Пт, 9:00–18:00 (GMT)",
    )
    show_consultation_cta = models.BooleanField(
        default=True,
        verbose_name="Показывать кнопку «Бесплатная консультация»",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("office_address"),
        FieldPanel("working_hours"),
        FieldPanel("show_consultation_cta"),
    ]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = []

    class Meta:
        verbose_name = "Страница «Контакты»"