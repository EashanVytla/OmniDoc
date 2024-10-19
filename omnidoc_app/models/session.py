import uuid
from django.db import models

class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)  # Required, references Patient model
    session_data = models.JSONField(blank=True, null=True)  # Stores conversation or data from the screening as a JSON object
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session for {self.patient.first_name} {self.patient.last_name} on {self.created_at}"

    class Meta:
        ordering = ['-created_at']
