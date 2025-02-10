from django.urls import path
from .views import main_view, doctor_patient_list_view, doctor_session_view, doctor_session_detail, start_recording

urlpatterns = [
    path('main/', main_view, name='main'),
    path('main/<uuid:session_id>/', main_view, name='main'),  # URL is handled in the app-level urls.py
    path('doctor/', doctor_patient_list_view, name='doctor_patient_list'),
    path('start-recording/<uuid:session_id>/', start_recording, name='start_recording'),
    path('doctor/<uuid:patient_id>/', doctor_session_view, name='doctor_session_list'),
    path('doctor/<uuid:patient_id>/<uuid:session_id>/', doctor_session_detail, name='doctor_session_detail'),
    path('receive-data/', start_recording, name='receive_data'),
]
