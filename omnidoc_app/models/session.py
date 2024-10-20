import uuid
from django.db import models

class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)  # Required, references Patient model
    session_data = models.JSONField(blank=True, null=True)  # Stores conversation or data from the screening as a JSON object
    doctor_reviewed = models.BooleanField(default=False)  # Tracks whether the report has been reviewed by a doctor
    notes = models.TextField(blank=True, null=True)  # Optional, additional notes by a doctor or assistant
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session for {self.patient.first_name} {self.patient.last_name} on {self.created_at}"

    class Meta:
        ordering = ['-created_at']
