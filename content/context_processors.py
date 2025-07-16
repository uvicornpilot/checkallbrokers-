from .models import SiteSettings


def site_settings(request):
    """Додає налаштування сайту до контексту всіх сторінок"""
    return {
        'site_settings': SiteSettings.objects.first()
    } 