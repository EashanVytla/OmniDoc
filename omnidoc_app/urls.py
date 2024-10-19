from django.urls import path
from .views import main_view, doctor_patient_list_view, start_recording

urlpatterns = [
    path('main/', main_view, name='main'),  # URL is handled in the app-level urls.py
    path('doctor/', doctor_patient_list_view, name='doctor_patient_list'),
     path('start-recording/', start_recording, name='start_recording'),
]
