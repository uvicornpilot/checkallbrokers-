from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forum.models import ForumCategory, ForumTopic
from django.utils.text import slugify
import random


class Command(BaseCommand):
    help = 'Створює демо-теми для форуму'

    def handle(self, *args, **options):
        # Отримуємо або створюємо адміністратора
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@brokercontrol.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Створено адміністратора: admin/admin123'))

        # Отримуємо категорії
        categories = ForumCategory.objects.filter(is_active=True)
        
        if not categories.exists():
            self.stdout.write(self.style.ERROR('Спочатку створіть категорії форуму!'))
            return

        # Демо-теми
        demo_topics = [
            {
                'title': 'Як перевірити брокера перед інвестуванням?',
                'content': '''
                <p>Доброго дня! Хочу поділитися досвідом перевірки брокерів перед інвестуванням.</p>
                
                <h4>Основні кроки перевірки:</h4>
                <ul>
                    <li>Перевірка ліцензії та регулювання</li>
                    <li>Аналіз відгуків та репутації</li>
                    <li>Вивчення умов торгівлі</li>
                    <li>Перевірка безпеки коштів</li>
                </ul>
                
                <p>Які ще методи перевірки ви використовуєте?</p>
                ''',
                'category_name': 'Перевірка брокерів'
            },
            {
                'title': 'Правові аспекти інвестування в Україні',
                'content': '''
                <p>Обговорюємо правові аспекти інвестування в Україні.</p>
                
                <h4>Важливі моменти:</h4>
                <ul>
                    <li>Податкове законодавство</li>
                    <li>Регулювання фінансових послуг</li>
                    <li>Захист прав інвесторів</li>
                    <li>Міжнародні угоди</li>
                </ul>
                
                <p>Чи маєте досвід з правовими питаннями інвестування?</p>
                ''',
                'category_name': 'Юридичні консультації'
            },
            {
                'title': 'Найкращі брокери для початківців',
                'content': '''
                <p>Рекомендації для новачків у світі інвестування.</p>
                
                <h4>Критерії вибору:</h4>
                <ul>
                    <li>Простота використання платформи</li>
                    <li>Навчальні матеріали</li>
                    <li>Підтримка клієнтів</li>
                    <li>Мінімальні депозити</li>
                </ul>
                
                <p>Які брокери найкраще підходять для початківців?</p>
                ''',
                'category_name': 'Рекомендації'
            },
            {
                'title': 'Як захиститися від шахрайських брокерів?',
                'content': '''
                <p>Важлива тема про захист від шахраїв у фінансовій сфері.</p>
                
                <h4>Ознаки шахрайських брокерів:</h4>
                <ul>
                    <li>Обіцянки гарантованого прибутку</li>
                    <li>Тиск на швидке рішення</li>
                    <li>Відсутність ліцензії</li>
                    <li>Складність виведення коштів</li>
                </ul>
                
                <p>Як ви захищаєтеся від шахраїв?</p>
                ''',
                'category_name': 'Безпека'
            },
            {
                'title': 'Порівняння брокерів: комісії та умови',
                'content': '''
                <p>Детальне порівняння різних брокерів за комісіями та умовами.</p>
                
                <h4>Що порівнюємо:</h4>
                <ul>
                    <li>Комісії за торгівлю</li>
                    <li>Спреды</li>
                    <li>Мінімальні депозити</li>
                    <li>Методи поповнення/виведення</li>
                </ul>
                
                <p>Які брокери мають найкращі умови?</p>
                ''',
                'category_name': 'Порівняння брокерів'
            }
        ]

        created_count = 0
        
        for topic_data in demo_topics:
            # Знаходимо категорію
            category = categories.filter(name__icontains=topic_data['category_name']).first()
            if not category:
                category = categories.first()  # Використовуємо першу доступну категорію
            
            # Створюємо унікальний slug
            base_slug = slugify(topic_data['title'])
            slug = base_slug
            counter = 1
            
            while ForumTopic.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            # Створюємо тему
            topic, created = ForumTopic.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': topic_data['title'],
                    'content': topic_data['content'],
                    'category': category,
                    'author': admin_user,
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Створено тему: {topic.title}')

        self.stdout.write(
            self.style.SUCCESS(f'Успішно створено {created_count} демо-тем!')
        ) 