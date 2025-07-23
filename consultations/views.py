from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .forms import ConsultationForm
from .models import LossReport


def consultation_view(request):
    """View для основної форми консультації"""
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            form.save()
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
        form.save()
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
            form.save()
            return JsonResponse({'success': True, 'message': 'Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в течение 24 часов.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'message': 'Неправильный метод запроса'})    