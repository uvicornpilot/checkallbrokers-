from django.shortcuts import render
from django.views.generic import TemplateView
from .models import SiteSection, Service, SiteSettings, HeroBanner, ContactInfo
from blog.models import Post
from django.utils import timezone
from consultations.forms import ConsultationForm


class HomeView(TemplateView):
    """Главная страница сайта"""
    template_name = 'content/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем активный hero банер
        hero_banner = HeroBanner.objects.filter(is_active=True).first()
        context['hero_banner'] = hero_banner
        
        # Получаем активные секции
        sections = SiteSection.objects.filter(is_active=True).order_by('order')
        context['sections'] = {section.name: section for section in sections}
        
        # Получаем услуги
        services = Service.objects.filter(is_active=True).order_by('order')
        context['services'] = services
        
        # Получаем последние посты блога
        latest_posts = Post.objects.filter(
            status='published',
            published_at__isnull=False,
            published_at__lte=timezone.now()
        ).order_by('-created_at')[:3]
        context['latest_posts'] = latest_posts
        
        # Добавляем форму консультации
        context['consultation_form'] = ConsultationForm()
        
        # Добавляем SEO метаданные
        if context.get('site_settings'):
            context['meta_title'] = context['site_settings'].meta_title
            context['meta_description'] = context['site_settings'].meta_description
            context['meta_keywords'] = context['site_settings'].meta_keywords
            context['og_image'] = context['site_settings'].og_image
            context['twitter_image'] = context['site_settings'].twitter_image
        else:
            context['meta_title'] = "Broker Control - Анализ и оценка брокерских компаний"
            context['meta_description'] = "Независимый информационно-аналитический проект по проверке брокеров и предоставлению юридических консультаций"
            context['meta_keywords'] = "брокер, проверка брокера, юридическая консультация, мошенничество, финансовые услуги"
        
        return context


class AboutView(TemplateView):
    """Страница 'О нас'"""
    template_name = 'content/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем секцию "О нас"
        about_section = SiteSection.objects.filter(name='about', is_active=True).first()
        context['about_section'] = about_section
        
        # SEO метаданные для страницы "О нас"
        context['meta_title'] = "О нас - Broker Control"
        context['meta_description'] = "Узнайте больше о команде Broker Control, нашей миссии и опыте в области проверки брокеров и юридических консультаций"
        context['meta_keywords'] = "о нас, команда, миссия, опыт, брокер контроль"
        
        return context


def get_section_content(section_name):
    """Получение контента секции"""
    try:
        section = SiteSection.objects.get(name=section_name, is_active=True)
        return {
            'title': section.title,
            'subtitle': section.subtitle,
            'content': section.content,
        }
    except SiteSection.DoesNotExist:
        return None
