from django.contrib import admin
from .models import Patient, Session, Report

# Register your models here.
admin.site.register(Patient)
admin.site.register(Session)
admin.site.register(Report)


