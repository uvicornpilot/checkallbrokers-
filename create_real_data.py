#!/usr/bin/env python
import os
import sys
import django
from django.utils import timezone
from datetime import datetime

# Налаштування Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'broker_control.settings')
django.setup()

from content.models import HeroBanner, SiteSection, Service, SiteSettings
from blog.models import Category, Tag, Post
from consultations.models import FormSettings, EmailTemplate

def create_hero_banner():
    """Створення головного банера"""
    hero_banner, created = HeroBanner.objects.get_or_create(
        title="Broker Control - Защита инвесторов",
        defaults={
            'subtitle': "Независимый анализ брокерских компаний",
            'description': "Получите профессиональную консультацию и защиту ваших инвестиций от мошеннических брокеров",
            'button_text': "Получить консультацию",
            'button_url': "#consult-form",
            'is_active': True,
            'order': 1
        }
    )
    if created:
        print(f"✅ Створено головний банер: {hero_banner.title}")
    else:
        print(f"ℹ️ Головний банер вже існує: {hero_banner.title}")
    return hero_banner

def create_site_sections():
    """Створення секцій сайту"""
    sections_data = [
        {
            'name': 'about',
            'title': 'О проекте',
            'subtitle': 'Независимый информационно-аналитический проект',
            'content': '''
            <p><strong>Broker Control</strong> - это независимый проект, созданный для защиты инвесторов от мошеннических брокерских компаний.</p>
            
            <p>Наша миссия - предоставить достоверную информацию о брокерах и помочь людям, пострадавшим от мошенничества в сфере финансовых услуг.</p>
            
            <h3>Что мы делаем:</h3>
            <ul>
                <li>Анализируем брокерские компании</li>
                <li>Предоставляем юридические консультации</li>
                <li>Помогаем в составлении жалоб и претензий</li>
                <li>Ведем базу данных мошеннических компаний</li>
            </ul>
            
            <p>Если вы пострадали от действий недобросовестного брокера, мы готовы помочь вам восстановить справедливость.</p>
            ''',
            'is_active': True,
            'order': 1
        },
        {
            'name': 'broker_banner',
            'title': 'Подобрать надежного брокера',
            'subtitle': 'Получите персональную рекомендацию от наших экспертов',
            'content': 'Наши специалисты помогут вам выбрать надежного брокера и избежать мошенников.',
            'is_active': True,
            'order': 2
        }
    ]
    
    for section_data in sections_data:
        section, created = SiteSection.objects.get_or_create(
            name=section_data['name'],
            defaults=section_data
        )
        if created:
            print(f"✅ Створено секцію: {section.get_name_display()}")
        else:
            print(f"ℹ️ Секція вже існує: {section.get_name_display()}")
    
    return SiteSection.objects.filter(is_active=True)

def create_services():
    """Створення послуг"""
    services_data = [
        {
            'title': 'Анализ брокера',
            'description': 'Проведем комплексный анализ брокерской компании, проверим лицензии и репутацию',
            'icon_svg': '''
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="48" height="48" rx="24" fill="#E8F5E8"/>
                <path d="M24 12L28.5 18.5L36 20L30 25.5L31.5 33L24 29.5L16.5 33L18 25.5L12 20L19.5 18.5L24 12Z" fill="#16C646"/>
            </svg>
            ''',
            'order': 1
        },
        {
            'title': 'Юридическая консультация',
            'description': 'Получите бесплатную консультацию от опытных юристов по защите ваших прав',
            'icon_svg': '''
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="48" height="48" rx="24" fill="#E8F5E8"/>
                <path d="M16 20H32M16 24H28M16 28H24M12 36V12C12 10.8954 12.8954 10 14 10H34C35.1046 10 36 10.8954 36 12V36C36 37.1046 35.1046 38 34 38H14C12.8954 38 12 37.1046 12 36Z" stroke="#16C646" stroke-width="2"/>
            </svg>
            ''',
            'order': 2
        },
        {
            'title': 'Составление документов',
            'description': 'Поможем составить жалобы, претензии и другие документы для защиты ваших интересов',
            'icon_svg': '''
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="48" height="48" rx="24" fill="#E8F5E8"/>
                <path d="M14 14H34M14 18H30M14 22H26M14 26H22M14 30H18M14 34H34" stroke="#16C646" stroke-width="2"/>
            </svg>
            ''',
            'order': 3
        }
    ]
    
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            title=service_data['title'],
            defaults=service_data
        )
        if created:
            print(f"✅ Створено послугу: {service.title}")
        else:
            print(f"ℹ️ Послуга вже існує: {service.title}")
    
    return Service.objects.filter(is_active=True)

def create_site_settings():
    """Створення налаштувань сайту"""
    settings, created = SiteSettings.objects.get_or_create(
        defaults={
            'site_name': 'Broker Control',
            'site_description': 'Независимый информационно-аналитический проект по проверке брокеров',
            'meta_title': 'Broker Control - Анализ и оценка брокерских компаний',
            'meta_description': 'Независимый информационно-аналитический проект по проверке брокеров и предоставлению юридических консультаций',
            'meta_keywords': 'брокер, проверка брокера, юридическая консультация, мошенничество, финансовые услуги',
            'contact_email': 'info@brokercontrol.ru',
            'contact_phone': '+7 (800) 123-45-67'
        }
    )
    if created:
        print(f"✅ Створено налаштування сайту")
    else:
        print(f"ℹ️ Налаштування сайту вже існують")
    return settings

def create_blog_data():
    """Створення даних для блогу"""
    # Створення категорії
    category, created = Category.objects.get_or_create(
        name='Проверка брокеров',
        defaults={
            'description': 'Статьи о проверке брокерских компаний',
            'is_active': True,
            'order': 1
        }
    )
    if created:
        print(f"✅ Створено категорію: {category.name}")
    
    # Створення тегів
    tags_data = ['Мошенничество', 'Брокер', 'Защита', 'Консультация']
    tags = []
    for tag_name in tags_data:
        tag, created = Tag.objects.get_or_create(
            name=tag_name,
            defaults={'is_active': True}
        )
        tags.append(tag)
        if created:
            print(f"✅ Створено тег: {tag.name}")
    
    # Створення статей
    posts_data = [
        {
            'title': 'Как проверить брокера перед инвестированием',
            'excerpt': 'Узнайте основные способы проверки надежности брокерской компании перед началом торговли',
            'content': '''
            <h2>Как проверить брокера перед инвестированием</h2>
            
            <p>Перед тем как доверить свои деньги брокерской компании, необходимо провести тщательную проверку. Вот основные шаги:</p>
            
            <h3>1. Проверка лицензии</h3>
            <p>Убедитесь, что у брокера есть действующая лицензия от регулирующего органа. В России это Центральный банк РФ.</p>
            
            <h3>2. Проверка репутации</h3>
            <p>Изучите отзывы клиентов, проверьте рейтинги и репутацию компании на специализированных сайтах.</p>
            
            <h3>3. Анализ условий</h3>
            <p>Внимательно изучите торговые условия, комиссии и минимальные депозиты.</p>
            
            <h3>4. Проверка безопасности</h3>
            <p>Убедитесь, что компания использует современные методы защиты данных и средств клиентов.</p>
            
            <p>Помните: лучше потратить время на проверку, чем потерять деньги из-за мошенников.</p>
            ''',
            'status': 'published',
            'published_at': timezone.now()
        },
        {
            'title': 'Топ-5 признаков мошеннического брокера',
            'excerpt': 'Научитесь распознавать мошенников в сфере брокерских услуг',
            'content': '''
            <h2>Топ-5 признаков мошеннического брокера</h2>
            
            <p>Мошеннические брокеры часто используют схожие схемы обмана. Вот основные признаки, на которые стоит обратить внимание:</p>
            
            <h3>1. Агрессивный маркетинг</h3>
            <p>Мошенники часто используют агрессивные методы продаж, обещают быстрые и гарантированные прибыли.</p>
            
            <h3>2. Отсутствие лицензии</h3>
            <p>Недобросовестные брокеры часто работают без лицензии или используют поддельные документы.</p>
            
            <h3>3. Скрытые комиссии</h3>
            <p>Мошенники скрывают реальные комиссии и дополнительные платежи в мелком шрифте.</p>
            
            <h3>4. Давление на клиентов</h3>
            <p>Попытки заставить клиента быстро принять решение без возможности обдумать условия.</p>
            
            <h3>5. Сложности с выводом средств</h3>
            <p>Мошенники создают искусственные препятствия для вывода средств клиентов.</p>
            
            <p>Если вы заметили эти признаки, лучше отказаться от сотрудничества с такой компанией.</p>
            ''',
            'status': 'published',
            'published_at': timezone.now()
        },
        {
            'title': 'Что делать, если вы стали жертвой мошенничества',
            'excerpt': 'Пошаговая инструкция для тех, кто пострадал от действий недобросовестного брокера',
            'content': '''
            <h2>Что делать, если вы стали жертвой мошенничества</h2>
            
            <p>Если вы стали жертвой мошеннического брокера, не отчаивайтесь. Есть способы защитить свои права и вернуть деньги.</p>
            
            <h3>1. Соберите доказательства</h3>
            <p>Сохраните все документы, переписку, скриншоты и другие доказательства взаимодействия с брокером.</p>
            
            <h3>2. Обратитесь в регулирующие органы</h3>
            <p>Подайте жалобу в Центральный банк РФ или другие регулирующие органы.</p>
            
            <h3>3. Обратитесь к юристу</h3>
            <p>Получите консультацию специалиста по финансовому праву.</p>
            
            <h3>4. Подайте заявление в полицию</h3>
            <p>Если есть признаки мошенничества, обратитесь в правоохранительные органы.</p>
            
            <h3>5. Обратитесь в суд</h3>
            <p>При необходимости подайте иск в суд для защиты своих прав.</p>
            
            <p>Помните: чем быстрее вы начнете действовать, тем больше шансов на успех.</p>
            ''',
            'status': 'published',
            'published_at': timezone.now()
        }
    ]
    
    for post_data in posts_data:
        post, created = Post.objects.get_or_create(
            title=post_data['title'],
            defaults={
                **post_data,
                'category': category,
                'slug': post_data['title'].lower().replace(' ', '-').replace(',', '').replace(':', '')
            }
        )
        if created:
            post.tags.set(tags[:2])  # Додаємо перші 2 теги
            print(f"✅ Створено статтю: {post.title}")
        else:
            print(f"ℹ️ Стаття вже існує: {post.title}")
    
    return Post.objects.filter(status='published')

def create_form_settings():
    """Створення налаштувань форми"""
    settings, created = FormSettings.objects.get_or_create(
        defaults={
            'title': 'Получить консультацию',
            'subtitle': 'Заполните форму ниже, и наш эксперт свяжется с вами в течение 24 часов для предоставления бесплатной консультации.',
            'modal_title': 'Потеряли деньги? Не знаете что делать?',
            'modal_subtitle': 'Получите бесплатную консультацию!',
            'admin_email': 'admin@brokercontrol.ru',
            'is_modal_enabled': True,
            'show_modal_after_seconds': 3
        }
    )
    if created:
        print(f"✅ Створено налаштування форми")
    else:
        print(f"ℹ️ Налаштування форми вже існують")
    return settings

def main():
    """Головна функція"""
    print("🚀 Початок створення тестових даних...")
    
    # Створення даних
    hero_banner = create_hero_banner()
    sections = create_site_sections()
    services = create_services()
    site_settings = create_site_settings()
    posts = create_blog_data()
    form_settings = create_form_settings()
    
    print("\n✅ Всі тестові дані створено успішно!")
    print(f"📊 Створено:")
    print(f"   - 1 головний банер")
    print(f"   - {sections.count()} секцій сайту")
    print(f"   - {services.count()} послуг")
    print(f"   - 1 налаштування сайту")
    print(f"   - {posts.count()} статей блогу")
    print(f"   - 1 налаштування форми")
    
    print("\n🌐 Тепер ви можете запустити сервер:")
    print("   python manage.py runserver")
    print("\n📝 Адмінка доступна за адресою:")
    print("   http://127.0.0.1:8000/admin/")

if __name__ == '__main__':
    main() 