from django.contrib import admin
from .models import Question, ConversationState

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "order", "is_active")

@admin.register(ConversationState)
class ConversationStateAdmin(admin.ModelAdmin):
    list_display = ("session", "current_step")  # ✅ fixed

    