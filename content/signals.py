from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import SiteSettings


@receiver(post_save, sender=SiteSettings)
@receiver(post_delete, sender=SiteSettings)
def clear_site_settings_cache(sender, instance, **kwargs):
    cache.delete(f'site_settings_{instance.site_id}')