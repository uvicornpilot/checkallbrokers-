from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'rating', 'text', 'parent', 'avatar', 'is_admin']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'review-form__input',
                'placeholder': 'Ваше имя',
                'required': True
            }),
            'rating': forms.Select(attrs={
                'class': 'review-form__select',
                'required': True
            }),
            'text': forms.Textarea(attrs={
                'class': 'review-form__textarea',
                'placeholder': 'Ваш отзыв...',
                'rows': 4,
                'required': True
            }),
            'parent': forms.HiddenInput(),
            'avatar': forms.TextInput(attrs={
                'class': 'review-form__input',
                'placeholder': '🙂 Аватар (эмодзи, опционально)'
            }),
            'is_admin': forms.CheckboxInput(attrs={
                'class': 'review-form__checkbox'
            })
        }
        labels = {
            'name': 'Имя *',
            'rating': 'Оценка *',
            'text': 'Отзыв *',
            'avatar': 'Аватар',
            'is_admin': 'Ответ администратора'
        } 