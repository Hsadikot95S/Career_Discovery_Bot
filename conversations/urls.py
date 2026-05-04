from django.urls import path
from .views import start_conversation, answer_question, next_question

urlpatterns = [
    path("start/", start_conversation),
    path("answer/", answer_question),
    path("next/<uuid:session_id>/", next_question),
]