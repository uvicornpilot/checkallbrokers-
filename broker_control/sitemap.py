from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Category, Tag


class StaticViewSitemap(Sitemap):
    priority = 0.9
    changefreq = "weekly"

    def items(self):
        # "content:about" убран — эта страница теперь Wagtail AboutPage
        # и уже попадает в sitemap через wagtail.contrib.sitemaps.Sitemap
        # (зарегистрирован в urls.py как "pages")
        return ["content:home", "forum:index", "consultations:consultation"]

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Category.objects.filter(is_active=True)

    def location(self, obj):
        return reverse("blog:category", kwargs={"slug": obj.slug})


class TagSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Tag.objects.all()

    def location(self, obj):
        return reverse("blog:tag", kwargs={"slug": obj.slug})