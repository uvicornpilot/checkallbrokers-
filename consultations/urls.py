from django.urls import path
from .views import consultation_view, submit_consultation_ajax, modal_consultation_view

app_name = 'consultations'

urlpatterns = [
    path('consultation/', consultation_view, name='consultation'),
    path('submit-ajax/', submit_consultation_ajax, name='submit_ajax'),
    path('modal-submit/', modal_consultation_view, name='modal_submit'),
] 