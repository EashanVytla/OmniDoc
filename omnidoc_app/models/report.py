import uuid
from django.db import models

class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.OneToOneField('Session', on_delete=models.CASCADE)  # Required, one-to-one relationship with Session model
    report_data = models.JSONField()  # Required, stores the report data as a JSON object
    generated_at = models.DateTimeField()  # Required, date and time when the report was generated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Report for session {self.session.id}, generated on {self.generated_at}"

    class Meta:
        ordering = ['-generated_at']
