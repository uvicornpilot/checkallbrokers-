from wagtail.models import Page

from blog.utils import slugify_ru


class AutoSlugPage(Page):
    """
    Автоматически генерирует slug из title через transliterate,
    как у блога — вместо стандартного Wagtail slugify(), который
    не транслитерирует кириллицу.
    """
    class Meta:
        abstract = True

    def full_clean(self, *args, **kwargs):
        if not self.pk or not self.slug:
            self.slug = slugify_ru(self.title)
        super().full_clean(*args, **kwargs)