import threading
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.conf import settings
from .forms import ConsultationForm
from .models import LossReport


def _send_via_resend(subject, html_content, to_email, reply_to=None):
    try:
        payload = {
            "from": settings.RESEND_FROM_EMAIL,
            "to": [to_email] if isinstance(to_email, str) else to_email,
            "subject": subject,
            "html": html_content,
        }
        if reply_to:
            payload["reply_to"] = reply_to

        resp = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=10,
        )
        if resp.status_code >= 400:
            print(f"⚠️ Resend ошибка ({resp.status_code}): {resp.text}")
        else:
            print(f"✅ Письмо отправлено: {to_email}")
    except Exception as e:
        print(f"⚠️ Resend исключение: {e}")


def _send_lead_notifications(instance):
    name = instance.name
    phone = instance.phone
    email = instance.email
    loss_amount = instance.loss_amount
    ticket_id = instance.pk

    def send_notifications():
        try:
            html_message = render_to_string('consultations/client_notification.html', {
                'name': name,
                'phone': phone,
                'email': email,
                'loss_amount': loss_amount,
                'ticket_id': ticket_id,
            })
            _send_via_resend(
                subject='Мы получили вашу заявку - Check All Broker',
                html_content=html_message,
                to_email=email,
            )
        except Exception as e:
            print(f'⚠️ Ошибка автоответа клиенту: {e}')

        try:
            admin_html = (
                f"<h2>Новая заявка — Consultation</h2>"
                f"<p><b>Номер:</b> №{ticket_id}</p>"
                f"<p><b>Имя:</b> {name}</p>"
                f"<p><b>Телефон:</b> {phone}</p>"
                f"<p><b>Email:</b> {email}</p>"
                f"<p><b>Сумма потерь:</b> {loss_amount if loss_amount else '—'}</p>"
                f"<p>Свяжитесь с клиентом как можно скорее.</p>"
            )
            recipients = getattr(settings, 'LEADS_EMAILS', [])
            if recipients:
                _send_via_resend(
                    subject=f'New Request - {name}',
                    html_content=admin_html,
                    to_email=recipients,
                    reply_to=email,
                )
        except Exception as e:
            print(f'⚠️ Ошибка уведомления админу: {e}')

    threading.Thread(target=send_notifications, daemon=True).start()

def consultation_view(request):
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            instance = form.save()
            _send_lead_notifications(instance)
            return JsonResponse({'success': True, 'message': 'Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ConsultationForm()

    return render(request, 'consultations/consultation.html', {'form': form})


@csrf_exempt
@require_http_methods(["POST"])
def submit_consultation_ajax(request):
    form = ConsultationForm(request.POST)
    if form.is_valid():
        instance = form.save()
        _send_lead_notifications(instance)
        return JsonResponse({
            'success': True,
            'message': 'Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время.'
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })


def modal_consultation_view(request):
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            instance = form.save()
            _send_lead_notifications(instance)
            return JsonResponse({'success': True, 'message': 'Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    return JsonResponse({'success': False, 'message': 'Неправильный метод запроса'})