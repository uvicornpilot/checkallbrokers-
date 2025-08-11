from django import template

register = template.Library()


@register.filter
def initial(name: str) -> str:
    if not name:
        return 'U'
    name = str(name).strip()
    return name[0].upper() if name else 'U'


@register.filter
def name_color(name: str) -> str:
    palette = [
        '#16C646', '#2E7D32', '#0088cc', '#0077b3', '#FFC107',
        '#9C27B0', '#E91E63', '#FF5722', '#3F51B5', '#009688'
    ]
    if not name:
        name = 'User'
    base = sum(ord(ch) for ch in str(name))
    return palette[base % len(palette)]


