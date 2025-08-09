from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """Категории для блога"""
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'slug': self.slug})


class Tag(models.Model):
    """Теги для блога"""
    name = models.CharField(max_length=50, verbose_name="Название тега")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Slug")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:tag', kwargs={'slug': self.slug})


class Post(models.Model):
    """Статьи блога"""
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликовано'),
    ]

    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    excerpt = models.TextField(max_length=500, verbose_name="Краткое описание")
    content = RichTextField(verbose_name="Контент")
    author = models.CharField(max_length=100, verbose_name="Автор", default="Admin")
    # Изображения
    featured_image = models.ImageField(upload_to='blog/', blank=True, verbose_name="Главное изображение")
    
    # Категории и теги
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='posts',
        verbose_name="Категория"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts', verbose_name="Теги")
    
    # Статус и публикация
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата публикации")
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True, verbose_name="Meta Title")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Meta Description")
    meta_keywords = models.CharField(max_length=500, blank=True, verbose_name="Meta Keywords")
    
    # Статистика
    views_count = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров")
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Автоматически генерируем SEO поля если они пустые
        if not self.meta_title:
            self.meta_title = self.title[:60]
        if not self.meta_description:
            self.meta_description = self.excerpt[:160]
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def increase_views(self):
        """Увеличение счетчика просмотров"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    @property
    def is_published(self):
        """Опубликована ли статья"""
        return self.status == 'published' and self.published_at is not None

    @property
    def reading_time(self):
        """Приблизительное время чтения (в минутах)"""
        words_per_minute = 200
        word_count = len(self.content.split())
        return max(1, round(word_count / words_per_minute))

    def get_previous_post(self):
        """Получить предыдущую статью"""
        return Post.objects.filter(
            status='published',
            published_at__lt=self.published_at
        ).order_by('-published_at').first()

    def get_next_post(self):
        """Получить следующую статью"""
        return Post.objects.filter(
            status='published',
            published_at__gt=self.published_at
        ).order_by('-published_at').first()

    def get_average_rating(self):
        """Получить среднюю оценку статьи"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0

    def get_reviews_count(self):
        """Получить количество одобренных отзывов"""
        return self.reviews.filter(is_approved=True).count()

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 звезда'),
        (2, '2 звезды'),
        (3, '3 звезды'),
        (4, '4 звезды'),
        (5, '5 звезд'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reviews', verbose_name="Статья")
    name = models.CharField(max_length=100, verbose_name="Имя")
    # Новый функционал: трединг ответов и аватар
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name="Родительский комментарий")
    avatar = models.CharField(max_length=10, blank=True, null=True, verbose_name="Аватар (эмодзи)")
    avatar_image = models.ImageField(upload_to='reviews/avatars/', blank=True, null=True, verbose_name="Аватар (фото)")
    is_admin = models.BooleanField(default=False, verbose_name="Ответ администратора")
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка"
    )
    text = models.TextField(verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_approved = models.BooleanField(default=False, verbose_name="Одобрено")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP адрес")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв от {self.name} на статью {self.post.title}"

    def get_rating_stars(self):
        """Вернуть HTML для отображения звезд"""
        stars = []
        for i in range(1, 6):
            if i <= self.rating:
                stars.append('<span class="star star--filled">★</span>')
            else:
                stars.append('<span class="star star--empty">☆</span>')
        return ''.join(stars)

    @property
    def approved_replies(self):
        """Одобренные ответы на этот отзыв"""
        return self.replies.filter(is_approved=True).order_by('created_at')
