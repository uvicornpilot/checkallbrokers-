from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'rating', 'text']
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
            })
        }
        labels = {
            'name': 'Имя *',
            'rating': 'Оценка *',
            'text': 'Отзыв *'
        } 