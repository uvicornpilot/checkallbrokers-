from django.core.management.base import BaseCommand
from forum.models import ForumTopic, ForumCategory
import re


class Command(BaseCommand):
    help = 'Виправляє slug у темах та категоріях форуму'

    def cyrillic_to_latin(self, text):
        """Конвертує кирилицю в латиницю для slug"""
        cyrillic_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'YO',
            'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'H', 'Ц': 'TS', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH',
            'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'YU', 'Я': 'YA'
        }
        
        result = ''
        for char in text:
            result += cyrillic_map.get(char, char)
        return result

    def create_slug(self, text):
        """Створює slug з тексту"""
        # Конвертуємо кирилицю
        text = self.cyrillic_to_latin(text)
        # Замінюємо пробіли на дефіси
        text = re.sub(r'\s+', '-', text)
        # Видаляємо всі символи крім букв, цифр та дефісів
        text = re.sub(r'[^a-zA-Z0-9\-]', '', text)
        # Видаляємо множинні дефіси
        text = re.sub(r'-+', '-', text)
        # Видаляємо дефіси на початку та в кінці
        text = text.strip('-')
        return text.lower()

    def handle(self, *args, **options):
        # Виправляємо slug для тем
        topics = ForumTopic.objects.all()
        fixed_count = 0
        
        for topic in topics:
            if not topic.slug or topic.slug.startswith('-') or topic.slug == '':
                # Створюємо slug з заголовка
                base_slug = self.create_slug(topic.title)
                if not base_slug:
                    base_slug = f'topic-{topic.id}'
                
                slug = base_slug
                counter = 1
                
                # Перевіряємо унікальність
                while ForumTopic.objects.filter(slug=slug).exclude(id=topic.id).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                topic.slug = slug
                topic.save(update_fields=['slug'])
                fixed_count += 1
                self.stdout.write(f'Виправлено slug для теми: {topic.title} -> {slug}')
        
        # Виправляємо slug для категорій
        categories = ForumCategory.objects.all()
        category_fixed = 0
        
        for category in categories:
            if not category.slug or category.slug.startswith('-') or category.slug == '':
                base_slug = self.create_slug(category.name)
                if not base_slug:
                    base_slug = f'category-{category.id}'
                
                slug = base_slug
                counter = 1
                
                while ForumCategory.objects.filter(slug=slug).exclude(id=category.id).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                category.slug = slug
                category.save(update_fields=['slug'])
                category_fixed += 1
                self.stdout.write(f'Виправлено slug для категорії: {category.name} -> {slug}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Успішно виправлено {fixed_count} тем та {category_fixed} категорій!'
            )
        ) 