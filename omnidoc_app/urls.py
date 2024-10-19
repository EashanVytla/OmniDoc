from django.urls import path
from .views import main_view, doctor_patient_list_view

urlpatterns = [
    path('main/', main_view, name='main'),  # URL is handled in the app-level urls.py
    path('doctor/', doctor_patient_list_view, name='doctor_patient_list')
]
