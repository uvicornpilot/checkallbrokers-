from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

# Wagtail
from wagtail.admin import urls as wagtail_admin_urls
from wagtail import urls as wagtail_urls
from wagtail.contrib.sitemaps import Sitemap as WagtailSitemap
from wagtail.documents import urls as wagtaildocs_urls

from .sitemap import (
    StaticViewSitemap,
    CategorySitemap,
    TagSitemap,
)

sitemaps = {
    "static": StaticViewSitemap,
    "pages": WagtailSitemap,
    "categories": CategorySitemap,
    "tags": TagSitemap,
}

urlpatterns = [
    # Админки
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtail_admin_urls)),

    # Wagtail Documents (даёт wagtaildocs_serve — без этого падает NoReverseMatch)
    path("documents/", include(wagtaildocs_urls)),

    # Твои приложения
    path("", include("content.urls")),
    path("blog/", include("blog.urls")),
    path("consultations/", include("consultations.urls")),
    path("forum/", include("forum.urls")),

    # Sitemap
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),

    # Robots
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain; charset=utf-8"),
    ),
    path(
        "llms.txt",
        TemplateView.as_view(template_name="llms.txt", content_type="text/plain; charset=utf-8"),
    ),

]

# Media/static — ОБЯЗАТЕЛЬНО до Wagtail catch-all
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Wagtail — ОБЯЗАТЕЛЬНО в самом конце!
urlpatterns += [
    path("", include(wagtail_urls)),
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


