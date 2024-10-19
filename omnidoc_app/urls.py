from django.urls import path
from .views import main_view

urlpatterns = [
    path('main/', main_view, name='main'),  # URL is handled in the app-level urls.py
]
