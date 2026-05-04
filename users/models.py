from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    education_level = models.CharField(max_length=100, blank=True)
    preferences = models.JSONField(default=dict, blank=True)