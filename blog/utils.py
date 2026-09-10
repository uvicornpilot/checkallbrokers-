from django.utils.text import slugify
from transliterate import translit


def slugify_ru(value):
    """Транслитерирует кириллицу в латиницу и создаёт корректный slug."""
    transliterated = translit(value, 'ru', reversed=True)
    return slugify(transliterated)