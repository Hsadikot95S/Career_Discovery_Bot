from django.urls import path
from .views import basic_recommendation, scored_recommendation, final_recommendation

urlpatterns = [
    path("recommendations/basic/<uuid:session_id>/", basic_recommendation),
    path("recommendations/scored/<uuid:session_id>/", scored_recommendation),
    path("recommendations/final/<uuid:session_id>/", final_recommendation),
]