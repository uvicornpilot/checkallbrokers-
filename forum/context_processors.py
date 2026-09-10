from django.conf import settings
from blog.models import BlogIndexPage

def forum_seo(request):
    """SEO контекст процессор для форума"""
    seo_context = {
        'site_name': getattr(settings, 'SITE_NAME', 'Broker Control'),
        'site_description': getattr(settings, 'SITE_DESCRIPTION', 'Профессиональные консультации по вопросам брокеров'),
        'site_keywords': getattr(settings, 'SITE_KEYWORDS', 'брокер, консультации, юридическая помощь'),
        'site_author': getattr(settings, 'SITE_AUTHOR', 'Broker Control Team'),
    }
    
    # Добавляем специфичные для форума мета-теги
    if hasattr(request, 'resolver_match') and request.resolver_match:
        app_name = request.resolver_match.app_name
        if app_name == 'forum':
            seo_context.update({
                'forum_title': 'Форум Broker Control - Обсуждение брокеров',
                'forum_description': 'Присоединяйтесь к обсуждению вопросов, связанных с брокерами. Получайте консультации и делитесь опытом.',
                'forum_keywords': 'форум, брокер, обсуждение, консультации, юридическая помощь, отзывы',
            })
    
    return seo_context



def site_settings(request):
    ...
    blog_index = BlogIndexPage.objects.live().first()
    return {
        'site_settings': settings,
        'blog_index_url': blog_index.url if blog_index else '/blog/',
    }