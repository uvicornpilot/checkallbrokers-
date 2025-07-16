from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import json

from .models import ConsultationRequest, FormSettings, EmailTemplate
from .forms import ConsultationRequestForm


def consultation_form(request):
    """Відображення форми консультації"""
    form = ConsultationRequestForm()
    form_settings = FormSettings.objects.first()
    
    context = {
        'form': form,
        'form_settings': form_settings,
    }
    return render(request, 'consultations/form.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def submit_consultation(request):
    """Обробка відправки форми консультації"""
    try:
        data = json.loads(request.body)
        form = ConsultationRequestForm(data)
        
        if form.is_valid():
            consultation = form.save()
            
            # Отримуємо налаштування форми
            form_settings = FormSettings.objects.first()
            
            # Відправляємо email користувачу
            if form_settings and form_settings.user_email_template:
                send_user_email(consultation, form_settings.user_email_template)
                consultation.email_sent_to_user = True
            
            # Відправляємо email адміністратору
            if form_settings and form_settings.admin_email_template:
                send_admin_email(consultation, form_settings.admin_email_template, form_settings.admin_email)
                consultation.email_sent_to_admin = True
            
            consultation.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Дякуємо! Ваша заявка успішно надіслана. Ми зв\'яжемося з вами найближчим часом.'
            })
        else:
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(error) for error in field_errors]
            
            return JsonResponse({
                'success': False,
                'errors': errors
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Помилка обробки даних'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Сталася помилка при обробці заявки'
        }, status=500)


def send_user_email(consultation, template):
    """Відправка email користувачу"""
    try:
        # Підготовка контексту для шаблону
        context = {
            'name': consultation.name,
            'phone': consultation.phone,
            'problem': consultation.problem,
            'created_at': consultation.created_at,
        }
        
        # Рендеримо HTML та текст версії
        html_content = template.html_content
        for key, value in context.items():
            html_content = html_content.replace(f'{{{{ {key} }}}}', str(value))
        
        text_content = strip_tags(html_content)
        
        # Відправляємо email
        send_mail(
            subject=template.subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[f'{consultation.name} <noreply@brokercontrol.com>'],
            html_message=html_content,
            fail_silently=False,
        )
        
    except Exception as e:
        print(f"Помилка відправки email користувачу: {e}")


def send_admin_email(consultation, template, admin_email):
    """Відправка email адміністратору"""
    try:
        # Підготовка контексту для шаблону
        context = {
            'name': consultation.name,
            'phone': consultation.phone,
            'problem': consultation.problem,
            'created_at': consultation.created_at,
        }
        
        # Рендеримо HTML та текст версію
        html_content = template.html_content
        for key, value in context.items():
            html_content = html_content.replace(f'{{{{ {key} }}}}', str(value))
        
        text_content = strip_tags(html_content)
        
        # Відправляємо email
        send_mail(
            subject=f"Нова заявка: {template.subject}",
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            html_message=html_content,
            fail_silently=False,
        )
        
    except Exception as e:
        print(f"Помилка відправки email адміністратору: {e}")


def get_form_settings(request):
    """API для отримання налаштувань форми"""
    form_settings = FormSettings.objects.first()
    if form_settings:
        return JsonResponse({
            'title': form_settings.title,
            'subtitle': form_settings.subtitle,
            'modal_title': form_settings.modal_title,
            'modal_subtitle': form_settings.modal_subtitle,
            'show_modal_after_seconds': form_settings.show_modal_after_seconds,
            'is_modal_enabled': form_settings.is_modal_enabled,
        })
    return JsonResponse({})
