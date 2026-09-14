from django.conf import settings
from django.core.paginator import Paginator
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify as django_slugify
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.images.models import Image
from wagtail.snippets.models import register_snippet
from wagtail.search import index
from django.utils import timezone
from .middleware import get_current_user

@register_snippet
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    visible_limit = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Лимит видимых статей в списке",
        help_text="Показывать в листинге категории только первые N опубликованных статей. "
                  "Новые статьи сверх лимита останутся доступны по прямой ссылке, в sitemap "
                  "и через поиск на сайте, но не будут видны в списке категории. "
                  "Оставьте пустым, чтобы показывать все.",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldPanel("is_active"),
        FieldPanel("order"),
        FieldPanel("visible_limit"),
    ]

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


CYRILLIC_MAP = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z',
    'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
    'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}


def transliterate_ru(text):
    return ''.join(CYRILLIC_MAP.get(ch, ch) for ch in text.lower())


@register_snippet
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    panels = [FieldPanel("name"), FieldPanel("slug")]

    def __str__(self):
        return self.name


class AuthorIndexPage(Page):
    template = "blog/author_list.html"
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [FieldPanel("intro")]

    max_count = 1
    subpage_types = ["blog.AuthorPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["authors"] = AuthorPage.objects.live().child_of(self)
        return context


class AuthorPage(Page):
    template = "blog/author_detail.html"

    user_account = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="author_profile",
    )
    photo = models.ForeignKey(
        Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
    )
    position = models.CharField(max_length=200, verbose_name="Должность")
    education = RichTextField(verbose_name="Образование")
    experience_years = models.PositiveIntegerField(verbose_name="Стаж (лет)")
    bio = RichTextField(verbose_name="О специалисте", blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)

    # --- новые поля ---
    specialization = models.CharField(
        max_length=255,
        verbose_name="Специализация",
        default="Compliance, аудит и регламент компаний",
        blank=True,
    )
    cases_count = models.PositiveIntegerField(
        verbose_name="Дел сопровождено",
        default=400,
        blank=True,
        null=True,
    )

    linkedin_url = models.URLField(
        verbose_name="LinkedIn",
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("user_account"),
        FieldPanel("photo"),
        FieldPanel("position"),
        FieldPanel("experience_years"),
        FieldPanel("cases_count"),
        FieldPanel("specialization"),
        FieldPanel("education"),
        FieldPanel("bio"),
        FieldPanel("linkedin_url"),




        MultiFieldPanel([FieldPanel("email"), FieldPanel("phone")], heading="Контакты"),
    ]

    parent_page_types = ["blog.AuthorIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Автор (юрист)"

    # в классе AuthorPage
    def get_articles(self):
        return (
            self.articles
            .live()
            .public()
            .order_by("-first_published_at")
        )

    def full_clean(self, *args, **kwargs):
        if not self.slug or any('а' <= ch <= 'я' for ch in self.slug.lower()):
            self.slug = django_slugify(transliterate_ru(self.title))
        super().full_clean(*args, **kwargs)

    def __str__(self):
        return self.title

class BlogIndexPage(Page):
    template = "blog/post_list.html"

    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [FieldPanel("intro")]

    max_count = 1
    subpage_types = ["blog.ArticlePage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        posts = ArticlePage.objects.live().child_of(self).order_by("-first_published_at")

        category_slug = request.GET.get("category")
        q = request.GET.get("q")

        if category_slug:
            posts = posts.filter(category__slug=category_slug)

            # Лимит видимых статей в листинге — не применяется при поиске (q),
            # чтобы новые статьи сверх лимита всё равно находились через поиск.
            if not q:
                category_obj = Category.objects.filter(slug=category_slug).first()
                if category_obj and category_obj.visible_limit:
                    visible_ids = list(
                        ArticlePage.objects.live().child_of(self)
                        .filter(category__slug=category_slug)
                        .order_by("first_published_at")
                        .values_list("id", flat=True)[:category_obj.visible_limit]
                    )
                    posts = posts.filter(id__in=visible_ids)

        tag_slug = request.GET.get("tag")
        if tag_slug:
            posts = posts.filter(tags__slug=tag_slug)

        if q:
            posts = posts.search(q)

        paginator = Paginator(posts, 9)
        context["posts"] = paginator.get_page(request.GET.get("page"))
        context["categories"] = Category.objects.filter(is_active=True)
        context["tags"] = Tag.objects.all()
        context["query"] = q or ""
        return context

class FAQItem(Orderable):
    """Вопрос-ответ в блоке FAQ статьи. Редактируется прямо в панели ArticlePage."""

    page = ParentalKey(
        "blog.ArticlePage", on_delete=models.CASCADE, related_name="faq_items",
    )
    question = models.CharField(max_length=300, verbose_name="Вопрос")
    answer = RichTextField(verbose_name="Ответ")

    panels = [
        FieldPanel("question"),
        FieldPanel("answer"),
    ]

class ArticlePage(Page):
    template = "blog/post_detail.html"

    excerpt = models.CharField(
        max_length=300, blank=True,
        help_text="Короткое описание для карточек статей и OG-превью",
    )

    from django.utils import timezone

    last_reviewed_at = models.DateField(
        default=timezone.now,
        verbose_name="Дата последней проверки юристом",
    )

    content = RichTextField()

    author = models.ForeignKey(
        AuthorPage, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="articles",
    )

    featured_image = models.ForeignKey(
        Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
    )
    featured_image_alt = models.CharField(max_length=200, blank=True)

    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="posts",
    )
    tags = ParentalManyToManyField(Tag, blank=True, related_name="posts")

    canonical_url = models.URLField(blank=True)
    views_count = models.PositiveIntegerField(default=0)

    disable_copy = models.BooleanField(default=True, verbose_name="Запретить копирование текста")
    disable_right_click = models.BooleanField(default=True, verbose_name="Блокировать контекстное меню")
    show_source_watermark = models.BooleanField(default=False, verbose_name="Скрытая метка авторства в тексте")

    show_risk_warning = models.BooleanField(
        default=True, verbose_name="Показывать предупреждение о рисках",
    )
    risk_warning_text = models.CharField(
        max_length=500, blank=True,
        default="Инвестиции сопряжены с риском потери средств. Проверяйте лицензию компании, её статус и T&C до начала работы — нелицензированные платформы часто выдают себя за регулируемых брокеров.",
        verbose_name="Текст предупреждения",
        help_text="Оставьте пустым, чтобы использовать текст по умолчанию",
    )

    is_company_review = models.BooleanField(
        default=True,
        verbose_name="Это обзор брокера/компании",
        help_text="Включите, если статья — обзор конкретного брокера. "
                  "Тогда на странице добавится микроразметка отзывов (AggregateRating) для поисковиков.",
    )
    company_name = models.CharField(
        max_length=200, blank=True,
        verbose_name="Название компании/брокера",
        help_text="Чистое название без 'Отзывы' и т.п. — используется в FAQ и микроразметке. "
                  "Если оставить пустым, будет использован заголовок страницы.",
    )
    show_faq = models.BooleanField(
        default=True,
        verbose_name="Показывать блок FAQ",
        help_text="Отключите, если статья не о конкретном брокере",
    )

    content_panels = Page.content_panels + [
        FieldPanel("excerpt"),
        MultiFieldPanel(
            [FieldPanel("show_risk_warning"), FieldPanel("risk_warning_text")],
            heading="Предупреждение о рисках",
        ),
        FieldPanel("content"),
        MultiFieldPanel(
            [FieldPanel("featured_image"), FieldPanel("featured_image_alt")],
            heading="Изображение статьи",
        ),
        FieldPanel("author"),
        FieldPanel("category"),
        FieldPanel("tags"),
        FieldPanel("is_company_review"),
        FieldPanel("company_name"),  # ← добавили эту строку
        FieldPanel("last_reviewed_at"),
        FieldPanel("show_faq"),
        MultiFieldPanel(
            [
                FieldPanel("disable_copy"),
                FieldPanel("disable_right_click"),
                FieldPanel("show_source_watermark"),
            ],
            heading="Защита контента",
        ),
        InlinePanel("faq_items", label="Вопрос-ответ (FAQ)"),
    ]

    promote_panels = Page.promote_panels + [FieldPanel("canonical_url")]

    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []

    search_fields = Page.search_fields + [
        index.SearchField("content"),
        index.SearchField("excerpt"),
        index.FilterField("category"),
    ]

    # --- ДОБАВЛЕНО: значения FAQ по умолчанию ---
    DEFAULT_FAQ = [
        (   "Что делать, если <strong class='faq-broker-name'>{broker}</strong> отклоняет или задерживает вывод средств?",
            "При первой задержке или отказе в выводе прекратите любые дополнительные платежи и "
            "зафиксируйте текущий статус. Первоочередной шаг — правовая фиксация фактов: сохраните "
            "банковские выписки, историю заявок в личном кабинете и переписку с поддержкой. "
            "Далее проводится аналитический аудит условий соглашения (T&C), чтобы определить, "
            "имеет ли место техническая задержка или намеренное нарушение регламента со стороны платформы."
        ),

        (
            "Чем вам поможет экспресс-аудит спорной ситуации с <strong class='faq-broker-name'>{broker}</strong>?",
            "Оставив заявку, вы получаете понятную дорожную карту и независимую оценку ситуации:"
            '<ul style="margin-top: 16px; margin-bottom: 0; padding-left: 20px;">'
            '<li style="margin-bottom: 10px;"><b>Экспертное резюме:</b> в каких именно пунктах брокер отступил от собственных правил (T&C) или регламента регулятора.</li>'
            '<li style="margin-bottom: 10px;"><b>Пошаговый план:</b> куда и в каком формате направить досудебную претензию для официального урегулирования.</li>'
            '<li style="margin-bottom: 0;"><b>Инструкция по фиксации:</b> какие выписки, чеки и скриншоты нужно сохранить прямо сейчас, пока не закрыт доступ к кабинету.</li>'
            "</ul>"
        ),
        (
            "Получу ли я гарантии возврата и как работает сервис?",
            "Проект не занимается прямым возвратом средств и не оказывает платное юридическое сопровождение. "
            "Ни одна независимая структура не может дать 100% гарантию возврата, так как итоговое решение всегда "
            "принимают официальные инстанции (банк, регулятор, суд). Мы гарантируем бескомпромиссно детальный аудит ваших документов, "
            "точную фиксацию каждого процедурного нарушения брокера и формирование исчерпывающей доказательной базы,"
            "с которой ваши шансы на успешное урегулирование становятся максимально высокими."
        ),
        (
            "Какие документы подготовить для бесплатного разбора ситуации по <strong class='faq-broker-name'>{broker}</strong>?",
            "Для первичного анализа ситуации и подготовки рекомендаций достаточно предоставить:"
            '<ul style="margin-top: 16px; margin-bottom: 0; padding-left: 20px;">'
            '<li style="margin-bottom: 10px;"><b>Регламент:</b> Клиентский регламент / Пользовательское соглашение (T&C) брокера.</li>'
            '<li style="margin-bottom: 10px;"><b>Скриншоты:</b> личного кабинета (баланс, история заявок на вывод, отклоненные транзакции).</li>'
            '<li style="margin-bottom: 10px;"><b>Выписки:</b> чеки или банковские выписки, подтверждающие факт и даты переводов.</li>'
            '<li style="margin-bottom: 0;"><b>Переписку:</b> диалоги со службой поддержки или менеджерами {broker}.</li>'
            "</ul>"
        ),
    ]

    class Meta:
        verbose_name = "Статья"

    def full_clean(self, *args, **kwargs):
        if not self.slug or any('а' <= ch <= 'я' for ch in self.slug.lower()):
            self.slug = django_slugify(transliterate_ru(self.title))
        if not self.company_name:
            self.company_name = self._extract_broker_name()
        super().full_clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.pk and not self.author_id:
            try:
                user = get_current_user()
                if user and getattr(user, "is_authenticated", False) and hasattr(user, "author_profile"):
                    self.author = user.author_profile
            except Exception:
                pass
        super().save(*args, **kwargs)

    @property
    def reading_time(self):
        words = len(self.content.split())
        return max(1, round(words / 200))

    def increase_views(self):
        ArticlePage.objects.filter(pk=self.pk).update(views_count=models.F("views_count") + 1)

    def get_average_rating(self):
        if not self.pk:
            return 0
        reviews = self.reviews.filter(status=Review.Status.APPROVED)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg("rating"))["rating__avg"], 1)
        return 0

    def get_reviews_count(self):
        if not self.pk:
            return 0
        return self.reviews.filter(status=Review.Status.APPROVED).count()

    # --- ДОБАВЛЕНО: метод получения FAQ ---
    def get_faq_items(self):
        """Возвращает FAQ, заданные редактором, либо значения по умолчанию с подставленным названием брокера."""
        custom = self.faq_items.all()
        broker_name = self.company_name or self._extract_broker_name()

        if custom.exists():
            return custom

        return [
            {"question": q.format(broker=broker_name), "answer": a}
            for q, a in self.DEFAULT_FAQ
        ]

    def _extract_broker_name(self):
        """Если company_name не заполнено — вырезает название брокера из title,
        отбрасывая суффиксы вида '- Отзывы', '- обзор брокера' и т.п."""
        import re
        title = self.title
        return re.split(r"\s*[-–—]\s", title, maxsplit=1)[0].strip()

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["post"] = self

        if self.pk:
            related = (
                ArticlePage.objects.live().filter(category=self.category).exclude(id=self.id)[:3]
            )
            if not related:
                # fallback: если по категории ничего не нашлось — берём последние статьи
                related = ArticlePage.objects.live().exclude(id=self.id).order_by("-first_published_at")[:3]
            context["related_posts"] = related

            reviews = self.reviews.filter(
                status=Review.Status.APPROVED, parent__isnull=True
            ).prefetch_related("replies")
            paginator = Paginator(reviews, 5)
            context["reviews"] = paginator.get_page(request.GET.get("review_page"))

            self.increase_views()
        else:
            context["related_posts"] = ArticlePage.objects.none()
            context["reviews"] = Paginator([], 5).get_page(1)

        context["popular_posts"] = ArticlePage.objects.live().order_by("-views_count")[:5]

        from .forms import ReviewForm
        context["review_form"] = ReviewForm()

        return context



class Review(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "На модерации"
        APPROVED = "approved", "Одобрено"
        REJECTED = "rejected", "Отклонено"

    RATING_CHOICES = [(i, f"{i} звезд") for i in range(1, 6)]

    post = models.ForeignKey(
        "blog.ArticlePage", on_delete=models.CASCADE, related_name="reviews",
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies",
    )

    name = models.CharField(max_length=100, verbose_name="Имя")
    avatar = models.CharField(max_length=10, blank=True)
    avatar_image = models.ImageField(upload_to="reviews/avatars/", blank=True, null=True)
    is_admin = models.BooleanField(default=False, verbose_name="Ответ от администратора")

    rating = models.IntegerField(
        choices=RATING_CHOICES, null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка",
        help_text="Только для корневых отзывов, не для ответов",
    )
    text = models.TextField(max_length=2000, verbose_name="Текст")
    created_at = models.DateTimeField(auto_now_add=True)
    helpful_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Отметок «Полезно»",
    )

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING,
        db_index=True, verbose_name="Статус",
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["created_at"]
        indexes = [models.Index(fields=["post", "status"])]

    def __str__(self):
        return f"{self.name} → {self.post.title if self.post_id else '—'}"

    # обратная совместимость с шаблоном/фильтрами, которые уже используют is_approved
    @property
    def is_approved(self):
        return self.status == self.Status.APPROVED

    @property
    def approved_replies(self):
        return self.replies.filter(status=self.Status.APPROVED).order_by("created_at")

