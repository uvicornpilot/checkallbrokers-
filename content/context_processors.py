from django.core.cache import cache
from wagtail.models import Site
from .models import SiteSettings

SETTINGS_CACHE_TIMEOUT = 60 * 15


def site_settings(request):
    site = Site.find_for_request(request)
    cache_key = f'site_settings_{site.id}'

    settings = cache.get(cache_key)
    if settings is None:
        settings = SiteSettings.load(request_or_site=site)  # передаём site, не request
        cache.set(cache_key, settings, SETTINGS_CACHE_TIMEOUT)

    return {'site_settings': settings}