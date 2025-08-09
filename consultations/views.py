from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from .forms import ConsultationForm
from .models import LossReport


def consultation_view(request):
    """View для основної форми консультації"""
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            instance = form.save()
            _send_lead_email(instance)
            return JsonResponse({'success': True, 'message': 'Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в течение 24 часов.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ConsultationForm()
    
    return render(request, 'consultations/consultation.html', {'form': form})


@csrf_exempt
@require_http_methods(["POST"])
def submit_consultation_ajax(request):
    """AJAX view для обробки форм консультацій"""
    form = ConsultationForm(request.POST)
    if form.is_valid():
        instance = form.save()
        _send_lead_email(instance)
        return JsonResponse({
            'success': True, 
            'message': 'Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в течение 24 часов.'
        })
    else:
        return JsonResponse({
            'success': False, 
            'errors': form.errors
        })


def modal_consultation_view(request):
    """View для модальної форми"""
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            instance = form.save()
            _send_lead_email(instance)
            return JsonResponse({'success': True, 'message': 'Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в течение 24 часов.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'message': 'Неправильный метод запроса'})    


def _send_lead_email(instance):
    """Отправка уведомления на почту с данными лида"""
    try:
        subject = "Новая заявка на консультацию"
        message_lines = [
            f"Имя: {getattr(instance, 'name', '')}",
            f"Телефон: {getattr(instance, 'phone', '')}",
            f"Email: {getattr(instance, 'email', '')}",
            f"Брокер: {getattr(instance, 'broker_name', '')}",
            f"Сумма потери: {getattr(instance, 'amount_lost', '')}",
            f"Описание проблемы: {getattr(instance, 'problem', '')}",
        ]
        message = "\n".join([line for line in message_lines if line.strip()])
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@forum-broker.com')
        recipient = getattr(settings, 'LEADS_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None) or 'info@forum-broker.com'
        send_mail(subject, message, from_email, [recipient], fail_silently=True)
    except Exception:
        # Не прерываем основной поток при ошибках отправки
        pass