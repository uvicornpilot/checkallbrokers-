from django.views.generic import TemplateView
from .models import SiteSection, Service, SiteSettings, HeroBanner, AboutUs, OurMission, OurTeam, OurValues
from blog.models import ArticlePage
from consultations.forms import ConsultationForm


class HomeView(TemplateView):
    template_name = 'content/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero_banner'] = HeroBanner.objects.filter(is_active=True).first()

        sections = SiteSection.objects.filter(is_active=True).order_by('order')
        context['sections'] = {section.name: section for section in sections}

        context['services'] = Service.objects.filter(is_active=True).order_by('order')
        context['latest_posts'] = ArticlePage.objects.live().order_by('-first_published_at')[:3]
        context['consultation_form'] = ConsultationForm()

        settings = SiteSettings.load(request_or_site=self.request)
        context['meta_title'] = settings.meta_title
        context['meta_description'] = settings.meta_description
        context['og_image'] = settings.og_image
        context['twitter_image'] = settings.twitter_image

        return context


class AboutView(TemplateView):
    template_name = 'content/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['about_section'] = AboutUs.objects.first()
        context['our_mission'] = OurMission.objects.all()
        context['our_team'] = OurTeam.objects.filter(is_active=True).order_by('order')
        context['our_values'] = OurValues.objects.all()

        context['meta_title'] = "О нас - Broker Control"
        context['meta_description'] = (
            "Узнайте больше о команде Broker Control, нашей миссии и опыте "
            "в области проверки брокеров и юридических консультаций"
        )

        return context