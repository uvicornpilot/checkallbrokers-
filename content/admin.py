from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from .models import Service, HeroBanner, SiteSection, OurTeam


class ServiceViewSet(SnippetViewSet):
    model = Service
    icon = "cog"
    menu_label = "Услуги"
    list_display = ["title", "is_active", "order"]
    list_filter = ["is_active"]


register_snippet(ServiceViewSet)