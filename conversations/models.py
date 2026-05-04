import uuid
from django.db import models
from user_sessions.models import Session
from .constants import ConversationStates

class Message(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("assistant", "Assistant"),
    )

    INPUT_TYPE = (
        ("text", "Text"),
        ("voice", "Voice"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    session = models.ForeignKey(
    Session,
    on_delete=models.CASCADE,
    related_name="messages"
)

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()

    input_type = models.CharField(
        max_length=10,
        choices=INPUT_TYPE,
        default="text"
    )

    created_at = models.DateTimeField(auto_now_add=True)

class ConversationState(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE,related_name="state")
    current_step = models.CharField(
        max_length=50,
        default=ConversationStates.START
    )
    step_index = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)

class Question(models.Model):
    CATEGORY_CHOICES = (
        ("PROFILE", "Profile"),
        ("INTEREST", "Interest"),
        ("DEPTH", "Depth"),
        ("VALIDATION", "Validation"),
    )

    text = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    order = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.category} - {self.text[:50]}"
    

    # def __str__(self):
    #     return f"{self.session.id} - {self.current_step}"
  