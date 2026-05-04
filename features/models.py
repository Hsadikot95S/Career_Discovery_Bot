import uuid
from django.db import models
from user_sessions.models import Session


class FeatureVector(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name="features"
    )

    # Core dimensions
    technical = models.FloatField(default=0.0)
    creativity = models.FloatField(default=0.0)
    analytical = models.FloatField(default=0.0)
    business = models.FloatField(default=0.0)
    research = models.FloatField(default=0.0)

    # Raw input
    source_text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"FeatureVector - {self.session.id}"