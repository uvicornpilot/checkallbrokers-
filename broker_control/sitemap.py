from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Post, Category, Tag
from django.utils import timezone

class StaticViewSitemap(Sitemap):
    priority = 0.9
    changefreq = 'weekly'

    def items(self):
        return ['content:home', 'content:about', 'blog:post_list', 'forum:index', 'consultations:consultation']

    def location(self, item):
        return reverse(item)

class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Post.objects.filter(status='published', published_at__isnull=False, published_at__lte=timezone.now())

    def lastmod(self, obj):
        return obj.updated_at

class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Category.objects.all()

class TagSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Tag.objects.all() 