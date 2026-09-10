from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel

from content.auto_slug_mixin import AutoSlugPage # поправьте путь под реальное расположение файла


class LegalPage(AutoSlugPage):
    body = RichTextField()

    content_panels = Page.content_panels + [FieldPanel("body")]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = []

    class Meta:
        verbose_name = "Юридическая страница"
