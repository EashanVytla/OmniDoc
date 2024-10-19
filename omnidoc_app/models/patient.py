import uuid
from django.db import models
from django.core.validators import MaxLengthValidator

class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50, validators=[MaxLengthValidator(50)])
    last_name = models.CharField(max_length=50, validators=[MaxLengthValidator(50)])
    dob = models.DateField()  # Date of Birth
    gender = models.CharField(max_length=20, blank=True, null=True)  # Optional
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Optional
    email = models.EmailField(unique=True, blank=True, null=True)  # Optional, Unique
    address = models.TextField(blank=True, null=True)  # Optional
    medical_history = models.JSONField(blank=True, null=True)  # Stores medical conditions, diagnosis dates, notes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['last_name', 'first_name']
