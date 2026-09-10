from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    # honeypot: обычный посетитель это поле не видит, боты — часто заполняют всё подряд
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'review-form__website',
            'autocomplete': 'off',
            'tabindex': '-1',
        }),
        label='',
    )

    class Meta:
        model = Review
        fields = ['name', 'rating', 'text', 'parent']

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
        }

        labels = {
            'name': 'Имя *',
            'rating': 'Оценка *',
            'text': 'Отзыв *',
        }

    def clean_website(self):
        value = self.cleaned_data.get('website')
        if value:
            raise forms.ValidationError('Ошибка отправки. Попробуйте ещё раз.')
        return value