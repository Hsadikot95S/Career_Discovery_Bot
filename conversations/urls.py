from django.urls import path
from .views import start_conversation, answer_question,respond

urlpatterns = [
    path("start/", start_conversation),
    path("answer/", answer_question),
    path("respond/<uuid:session_id>/", respond),
]