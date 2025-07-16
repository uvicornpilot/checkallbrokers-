from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.utils.text import slugify


class ForumCategory(models.Model):
    """Категория форума"""
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Иконка (emoji)")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    # SEO поля
    meta_title = models.CharField(max_length=60, blank=True, verbose_name="Meta Title")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Meta Description")
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name="Meta Keywords")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Категория форума"
        verbose_name_plural = "Категории форума"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('forum:category_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            # Конвертуємо кирилицю в латиницю для slug
            import re
            cyrillic_map = {
                'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
                'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
                'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
                'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
                'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'YO',
                'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
                'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
                'Ф': 'F', 'Х': 'H', 'Ц': 'TS', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH',
                'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'YU', 'Я': 'YA'
            }
            
            result = ''
            for char in self.name:
                result += cyrillic_map.get(char, char)
            
            # Замінюємо пробіли на дефіси
            result = re.sub(r'\s+', '-', result)
            # Видаляємо всі символи крім букв, цифр та дефісів
            result = re.sub(r'[^a-zA-Z0-9\-]', '', result)
            # Видаляємо множинні дефіси
            result = re.sub(r'-+', '-', result)
            # Видаляємо дефіси на початку та в кінці
            result = result.strip('-')
            
            if result:
                self.slug = result.lower()
            else:
                self.slug = f'category-{self.id}'
        super().save(*args, **kwargs)

    def get_topics_count(self):
        return self.topics.filter(is_active=True).count()

    def get_posts_count(self):
        return self.topics.filter(is_active=True).aggregate(
            total=models.Count('posts', filter=models.Q(posts__is_approved=True))
        )['total'] or 0


class ForumTopic(models.Model):
    """Тема форума"""
    STATUS_CHOICES = [
        ('open', 'Открытая'),
        ('closed', 'Закрытая'),
        ('pinned', 'Закрепленная'),
    ]

    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL")
    content = RichTextField(verbose_name="Содержание")
    category = models.ForeignKey(
        ForumCategory, 
        on_delete=models.CASCADE, 
        related_name='topics',
        verbose_name="Категория"
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='forum_topics',
        verbose_name="Автор"
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='open',
        verbose_name="Статус"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    # SEO поля
    meta_title = models.CharField(max_length=60, blank=True, verbose_name="Meta Title")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Meta Description")
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name="Meta Keywords")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Тема форума"
        verbose_name_plural = "Темы форума"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('forum:topic_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            # Конвертуємо кирилицю в латиницю для slug
            import re
            cyrillic_map = {
                'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
                'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
                'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
                'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
                'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'YO',
                'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
                'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
                'Ф': 'F', 'Х': 'H', 'Ц': 'TS', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH',
                'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'YU', 'Я': 'YA'
            }
            
            result = ''
            for char in self.title:
                result += cyrillic_map.get(char, char)
            
            # Замінюємо пробіли на дефіси
            result = re.sub(r'\s+', '-', result)
            # Видаляємо всі символи крім букв, цифр та дефісів
            result = re.sub(r'[^a-zA-Z0-9\-]', '', result)
            # Видаляємо множинні дефіси
            result = re.sub(r'-+', '-', result)
            # Видаляємо дефіси на початку та в кінці
            result = result.strip('-')
            
            if result:
                self.slug = result.lower()
            else:
                self.slug = f'topic-{self.id}'
        super().save(*args, **kwargs)

    def get_posts_count(self):
        return self.posts.filter(is_approved=True).count()

    def get_last_post(self):
        return self.posts.filter(is_approved=True).order_by('-created_at').first()


class ForumPost(models.Model):
    """Пост/комментарий в форуме"""
    topic = models.ForeignKey(
        ForumTopic, 
        on_delete=models.CASCADE, 
        related_name='posts',
        verbose_name="Тема"
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='forum_posts',
        verbose_name="Автор",
        null=True,
        blank=True
    )
    # Поля для анонимных комментариев
    anonymous_name = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Имя (анонимно)"
    )
    anonymous_email = models.EmailField(
        blank=True, 
        verbose_name="Email (анонимно)"
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='replies',
        verbose_name="Родительский комментарий"
    )
    content = RichTextField(verbose_name="Содержание")
    is_approved = models.BooleanField(default=False, verbose_name="Одобрено")
    is_moderated = models.BooleanField(default=False, verbose_name="Промодерировано")
    # SEO поля для постов
    meta_title = models.CharField(max_length=60, blank=True, verbose_name="Meta Title")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Meta Description")
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name="Meta Keywords")
    # Додаткові SEO поля
    og_title = models.CharField(max_length=60, blank=True, verbose_name="Open Graph Title")
    og_description = models.CharField(max_length=160, blank=True, verbose_name="Open Graph Description")
    og_image = models.ImageField(upload_to='forum/og_images/', blank=True, verbose_name="Open Graph Image")
    canonical_url = models.URLField(blank=True, verbose_name="Canonical URL")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Пост форума"
        verbose_name_plural = "Посты форума"
        ordering = ['created_at']

    def __str__(self):
        if self.author:
            return f"Пост от {self.author.username} в теме {self.topic.title}"
        else:
            return f"Пост от {self.anonymous_name} в теме {self.topic.title}"

    def get_author_name(self):
        """Получить имя автора"""
        if self.author:
            return self.author.username
        else:
            return self.anonymous_name or "Аноним"

    def get_absolute_url(self):
        return f"{self.topic.get_absolute_url()}#post-{self.id}"

    def get_replies_count(self):
        return self.replies.filter(is_approved=True).count()

    def get_all_replies(self):
        """Отримати всі відповіді (включаючи вкладені)"""
        replies = []
        for reply in self.replies.filter(is_approved=True).order_by('created_at'):
            replies.append(reply)
            replies.extend(reply.get_all_replies())
        return replies

    def save(self, *args, **kwargs):
        """Автоматическое заполнение SEO полей"""
        if not self.meta_title:
            # Генерируем meta title из содержимого
            from django.utils.html import strip_tags
            clean_content = strip_tags(self.content)
            if len(clean_content) > 50:
                self.meta_title = clean_content[:50] + "..."
            else:
                self.meta_title = clean_content
        
        if not self.meta_description:
            # Генерируем meta description
            from django.utils.html import strip_tags
            clean_content = strip_tags(self.content)
            if len(clean_content) > 150:
                self.meta_description = clean_content[:150] + "..."
            else:
                self.meta_description = clean_content
        
        if not self.og_title:
            self.og_title = self.meta_title
        
        if not self.og_description:
            self.og_description = self.meta_description
        
        super().save(*args, **kwargs)

    def get_seo_data(self):
        """Получить SEO данные для поста"""
        return {
            'title': self.meta_title or f"Ответ в теме: {self.topic.title}",
            'description': self.meta_description or f"Ответ пользователя {self.get_author_name()} в теме {self.topic.title}",
            'keywords': self.meta_keywords or f"форум, {self.topic.category.name}, {self.topic.title}",
            'og_title': self.og_title or self.meta_title,
            'og_description': self.og_description or self.meta_description,
            'og_image': self.og_image.url if self.og_image else None,
            'canonical_url': self.canonical_url or self.get_absolute_url(),
        }


class ForumModerationLog(models.Model):
    """Лог модерации"""
    ACTION_CHOICES = [
        ('approve', 'Одобрено'),
        ('reject', 'Отклонено'),
        ('edit', 'Отредактировано'),
        ('delete', 'Удалено'),
    ]

    moderator = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='moderation_actions',
        verbose_name="Модератор"
    )
    post = models.ForeignKey(
        ForumPost, 
        on_delete=models.CASCADE, 
        related_name='moderation_logs',
        verbose_name="Пост"
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name="Дія")
    reason = models.TextField(blank=True, verbose_name="Причина")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")

    class Meta:
        verbose_name = "Лог модерации"
        verbose_name_plural = "Логи модерации"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_display()} - {self.post}"


class ForumNotification(models.Model):
    """Уведомления форума"""
    TYPE_CHOICES = [
        ('post_approved', 'Пост одобрен'),
        ('post_rejected', 'Пост отклонен'),
        ('reply_received', 'Получен ответ'),
        ('topic_reply', 'Ответ в теме'),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='forum_notifications',
        verbose_name="Пользователь"
    )
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Тип")
    post = models.ForeignKey(
        ForumPost, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        verbose_name="Пост"
    )
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = "Уведомление форума"
        verbose_name_plural = "Уведомления форума"
        ordering = ['-created_at']

    def __str__(self):
        return f"Уведомление для {self.user.username} - {self.get_notification_type_display()}"
