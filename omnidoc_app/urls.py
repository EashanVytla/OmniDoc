from django.urls import path
from .views import main_view, doctor_patient_list_view, doctor_session_view, doctor_session_detail

urlpatterns = [
    path('main/', main_view, name='main'),  # URL is handled in the app-level urls.py
    path('doctor/', doctor_patient_list_view, name='doctor_patient_list'),
    path('start-recording/', start_recording, name='start_recording'),
    path('doctor/<uuid:patient_id>/', doctor_session_view, name='doctor_session_list'),
    path('doctor/<uuid:patient_id>/<uuid:session_id>/', doctor_session_detail, name='doctor_session_detail'),
    path('start-recording/', start_recording, name='start_recording'),
    path('receive-data/', start_recording, name='receive_data'),
]
