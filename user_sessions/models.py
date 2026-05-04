import uuid
from django.db import models
from django.conf import settings

from users.models import User

class Session(models.Model):
    SESSION_TYPES = (
        ("stream", "Stream Selection"),
        ("career", "Career Selection"),
    )

    STATUS_CHOICES = (
        ("active", "Active"),
        ("completed", "Completed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    current_step = models.IntegerField(default=0)
    total_steps = models.IntegerField(default=30)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.session_type}"