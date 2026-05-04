from django.db import models
from user_sessions.models import Session

class DomainScore(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="domain_scores")

    domain = models.CharField(max_length=100)
    score = models.FloatField()
    rank = models.IntegerField()

    def __str__(self):
        return f"{self.domain} - {self.score}"