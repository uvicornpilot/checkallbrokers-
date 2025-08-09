from django import forms
from .models import LossReport


class ConsultationForm(forms.ModelForm):


    class Meta:
        model = LossReport
        fields = ['name', 'phone', 'email', 'loss_amount']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-group__input',
                'placeholder': 'Ваше ім\'я'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-group__input',
                'placeholder': '+380XXXXXXXXX'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-group__input',
                'placeholder': 'your@email.com'
            }),
            'loss_amount': forms.NumberInput(attrs={
                'class': 'form-group__input',
                'placeholder': 'Наприклад: 1000'
            }),
        }
        labels = {
            'name': 'Ім\'я *',
            'phone': 'Телефон *',
            'email': 'Email *',
            'loss_amount': 'Сума втрат',
        }
