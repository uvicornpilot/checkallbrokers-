from django import forms
from django.core.validators import RegexValidator
from .models import ConsultationRequest


class ConsultationRequestForm(forms.ModelForm):
    """Форма для заявки на консультацію"""
    
    class Meta:
        model = ConsultationRequest
        fields = ['name', 'phone', 'problem']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-group__input',
                'placeholder': 'Ваше ім\'я'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-group__input',
                'placeholder': '+380XXXXXXXXX'
            }),
            'problem': forms.Textarea(attrs={
                'class': 'form-group__textarea',
                'rows': 4,
                'placeholder': 'Розкажіть детально про вашу ситуацію з брокером...'
            })
        }
        labels = {
            'name': 'Ім\'я *',
            'phone': 'Телефон *',
            'problem': 'Опишіть вашу проблему *'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо валідацію для телефону
        self.fields['phone'].validators.append(
            RegexValidator(
                regex=r'^[\+]?[0-9\s\-\(\)]{10,}$',
                message='Введіть коректний номер телефону'
            )
        )

    def clean_phone(self):
        """Очищення та валідація телефону"""
        phone = self.cleaned_data['phone']
        # Видаляємо всі символи крім цифр, +, -, (, ), пробілів
        phone = ''.join(c for c in phone if c.isdigit() or c in '+-() ')
        
        if len(phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) < 10:
            raise forms.ValidationError('Номер телефону повинен містити мінімум 10 цифр')
        
        return phone

    def clean_problem(self):
        """Валідація опису проблеми"""
        problem = self.cleaned_data['problem']
        if len(problem.strip()) < 10:
            raise forms.ValidationError('Опис проблеми повинен містити мінімум 10 символів')
        return problem 