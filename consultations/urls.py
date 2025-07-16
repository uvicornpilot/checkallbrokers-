from django.urls import path
from . import views

app_name = 'consultations'

urlpatterns = [
    path('form/', views.consultation_form, name='form'),
    path('submit/', views.submit_consultation, name='submit'),
    path('settings/', views.get_form_settings, name='settings'),
] 