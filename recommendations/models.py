from django.db import models
from user_sessions.models import Session

class Recommendation(models.Model):
    TYPE_CHOICES = (
        ("career", "Career"),
        ("degree", "Degree"),
    )

    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="recommendations")

    rec_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)

    metadata = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.title} ({self.rec_type})"