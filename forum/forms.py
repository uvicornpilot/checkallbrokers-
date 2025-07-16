from django import forms
from django.contrib.auth.models import User
from .models import ForumTopic, ForumPost, ForumCategory


class ForumTopicForm(forms.ModelForm):
    """Форма для создания новой темы"""
    class Meta:
        model = ForumTopic
        fields = ['title', 'category', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Заголовок темы'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Содержание темы...'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показуємо тільки активні категорії
        self.fields['category'].queryset = ForumCategory.objects.filter(is_active=True)


class ForumPostForm(forms.ModelForm):
    """Форма для создания комментария"""
    anonymous_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваше имя'
        }),
        label="Ваше имя"
    )
    anonymous_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваш email'
        }),
        label="Ваш email"
    )
    
    class Meta:
        model = ForumPost
        fields = ['content', 'anonymous_name', 'anonymous_email']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Напишите ваш комментарий...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.topic = kwargs.pop('topic', None)
        self.parent = kwargs.pop('parent', None)
        self.author = kwargs.pop('author', None)
        super().__init__(*args, **kwargs)
        
        # Если пользователь авторизован, скрываем поля для анонимных комментариев
        if self.author:
            self.fields['anonymous_name'].widget = forms.HiddenInput()
            self.fields['anonymous_email'].widget = forms.HiddenInput()
        else:
            # Для анонимных пользователей делаем поля обязательными
            self.fields['anonymous_name'].required = True
            self.fields['anonymous_email'].required = True
    
    def save(self, author=None, commit=True):
        post = super().save(commit=False)
        if self.topic:
            post.topic = self.topic
        if self.parent:
            post.parent = self.parent
        if author:
            post.author = author
        if commit:
            post.save()
        return post


class ForumSearchForm(forms.Form):
    """Форма поиска по форуму"""
    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по форуму...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=ForumCategory.objects.filter(is_active=True),
        required=False,
        empty_label="Все категории",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    search_in = forms.ChoiceField(
        choices=[
            ('all', 'Везде'),
            ('topics', 'Только темы'),
            ('posts', 'Только комментарии'),
        ],
        initial='all',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class ForumModerationForm(forms.Form):
    """Форма для модерации постов"""
    action = forms.ChoiceField(
        choices=[
            ('approve', 'Одобрить'),
            ('reject', 'Отклонить'),
            ('delete', 'Удалить'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    reason = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Причина (необязательно)'
        })
    ) 