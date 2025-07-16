from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forum.models import ForumCategory, ForumTopic, ForumPost
from django.utils.text import slugify
import random


class Command(BaseCommand):
    help = 'Создает демо-данные для форума'

    def handle(self, *args, **options):
        self.stdout.write('Создание демо-данных для форума...')

        # Создаем суперпользователя если его нет
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write('Создан суперпользователь: admin/admin123')

        admin_user = User.objects.get(username='admin')

        # Создаем категории
        categories_data = [
            {
                'name': 'Общие вопросы',
                'description': 'Обсуждение общих вопросов, связанных с брокерами и торговлей',
                'icon': '💬',
                'order': 1
            },
            {
                'name': 'Мошенничество и обман',
                'description': 'Истории о мошеннических брокерах и способах защиты',
                'icon': '⚠️',
                'order': 2
            },
            {
                'name': 'Юридическая помощь',
                'description': 'Вопросы по юридическим аспектам и восстановлению средств',
                'icon': '⚖️',
                'order': 3
            },
            {
                'name': 'Отзывы о брокерах',
                'description': 'Отзывы и рейтинги брокерских компаний',
                'icon': '⭐',
                'order': 4
            },
            {
                'name': 'Советы и рекомендации',
                'description': 'Полезные советы по работе с брокерами',
                'icon': '💡',
                'order': 5
            }
        ]

        categories = []
        for cat_data in categories_data:
            category, created = ForumCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'order': cat_data['order'],
                    'meta_title': f"{cat_data['name']} - Форум Broker Control",
                    'meta_description': cat_data['description'],
                    'meta_keywords': f"форум, {cat_data['name'].lower()}, брокер, обсуждение"
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Создана категория: {category.name}')

        # Создаем темы
        topics_data = [
            {
                'title': 'Как проверить брокера перед началом работы?',
                'content': '''
                <h3>Важные моменты при проверке брокера:</h3>
                <ul>
                    <li>Проверьте лицензию и регулирование</li>
                    <li>Изучите отзывы других трейдеров</li>
                    <li>Проверьте историю компании</li>
                    <li>Убедитесь в наличии страховки</li>
                </ul>
                <p>Делитесь своим опытом проверки брокеров!</p>
                ''',
                'category': categories[0]
            },
            {
                'title': 'Мошеннический брокер не выводит деньги',
                'content': '''
                <h3>Что делать если брокер не выводит деньги:</h3>
                <ol>
                    <li>Соберите все документы и переписку</li>
                    <li>Обратитесь в регулирующие органы</li>
                    <li>Подайте жалобу в правоохранительные органы</li>
                    <li>Обратитесь за юридической помощью</li>
                </ol>
                <p>Расскажите свою историю и получите совет!</p>
                ''',
                'category': categories[1]
            },
            {
                'title': 'Нужна помощь в составлении претензии',
                'content': '''
                <h3>Помощь в составлении претензии к брокеру</h3>
                <p>У кого есть опыт составления претензий к брокерам? Поделитесь шаблонами и советами.</p>
                <p>Какие документы нужно приложить к претензии?</p>
                ''',
                'category': categories[2]
            },
            {
                'title': 'Отзыв о брокере FXPro',
                'content': '''
                <h3>Мой опыт работы с FXPro</h3>
                <p>Работаю с этим брокером уже 2 года. В целом доволен:</p>
                <ul>
                    <li>Быстрый вывод средств</li>
                    <li>Хорошая поддержка</li>
                    <li>Стабильная платформа</li>
                </ul>
                <p>Есть ли у кого-то еще опыт с этим брокером?</p>
                ''',
                'category': categories[3]
            },
            {
                'title': 'Советы новичкам по выбору брокера',
                'content': '''
                <h3>Основные критерии выбора брокера для новичков:</h3>
                <ul>
                    <li>Надежность и репутация</li>
                    <li>Удобство платформы</li>
                    <li>Размер минимального депозита</li>
                    <li>Качество поддержки</li>
                </ul>
                <p>Какие еще критерии важны по вашему мнению?</p>
                ''',
                'category': categories[4]
            }
        ]

        topics = []
        for topic_data in topics_data:
            topic, created = ForumTopic.objects.get_or_create(
                title=topic_data['title'],
                defaults={
                    'slug': slugify(topic_data['title']),
                    'content': topic_data['content'],
                    'category': topic_data['category'],
                    'author': admin_user,
                    'meta_title': f"{topic_data['title']} - Форум Broker Control",
                    'meta_description': f"Обсуждение: {topic_data['title']}",
                    'meta_keywords': f"форум, брокер, {topic_data['category'].name.lower()}, обсуждение"
                }
            )
            topics.append(topic)
            if created:
                self.stdout.write(f'Создана тема: {topic.title}')

        # Создаем комментарии
        comments_data = [
            {
                'content': 'Отличная статья! Я тоже всегда проверяю лицензию перед началом работы.',
                'topic': topics[0]
            },
            {
                'content': 'Спасибо за советы! Очень полезная информация для новичков.',
                'topic': topics[0]
            },
            {
                'content': 'У меня была похожая ситуация. Обратился в регулятор и через месяц получил деньги обратно.',
                'topic': topics[1]
            },
            {
                'content': 'Главное - не паниковать и действовать по закону. Соберите все документы.',
                'topic': topics[1]
            },
            {
                'content': 'У меня есть шаблон претензии. Могу поделиться, если нужно.',
                'topic': topics[2]
            },
            {
                'content': 'FXPro действительно хороший брокер. Работаю с ними уже год.',
                'topic': topics[3]
            },
            {
                'content': 'Согласен с автором. FXPro один из самых надежных брокеров.',
                'topic': topics[3]
            },
            {
                'content': 'Для новичков еще важно обратить внимание на обучающие материалы.',
                'topic': topics[4]
            },
            {
                'content': 'И не забывайте про демо-счет для практики!',
                'topic': topics[4]
            }
        ]

        for comment_data in comments_data:
            post, created = ForumPost.objects.get_or_create(
                content=comment_data['content'],
                topic=comment_data['topic'],
                defaults={
                    'author': admin_user,
                    'is_approved': True,
                    'is_moderated': True
                }
            )
            if created:
                self.stdout.write(f'Создан комментарий в теме: {comment_data["topic"].title}')

        # Создаем анонимные комментарии
        anonymous_comments = [
            {
                'content': 'Анонимный комментарий: Спасибо за информацию!',
                'anonymous_name': 'Аноним',
                'anonymous_email': 'anon@example.com',
                'topic': topics[0]
            },
            {
                'content': 'Еще один анонимный комментарий: Очень полезно!',
                'anonymous_name': 'Гость',
                'anonymous_email': 'guest@example.com',
                'topic': topics[1]
            }
        ]

        for comment_data in anonymous_comments:
            post, created = ForumPost.objects.get_or_create(
                content=comment_data['content'],
                topic=comment_data['topic'],
                defaults={
                    'anonymous_name': comment_data['anonymous_name'],
                    'anonymous_email': comment_data['anonymous_email'],
                    'is_approved': True,
                    'is_moderated': True
                }
            )
            if created:
                self.stdout.write(f'Создан анонимный комментарий в теме: {comment_data["topic"].title}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Демо-данные созданы успешно!\n'
                f'Категорий: {len(categories)}\n'
                f'Тем: {len(topics)}\n'
                f'Комментариев: {len(comments_data) + len(anonymous_comments)}'
            )
        ) 