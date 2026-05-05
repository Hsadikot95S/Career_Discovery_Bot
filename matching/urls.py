from django.urls import path
from .views import get_recommendation, final_recommendation,hybrid_result

urlpatterns = [
    path("result/<uuid:session_id>/", get_recommendation),
    path("final/<uuid:session_id>/", final_recommendation),
    path("hybrid/<uuid:session_id>/", hybrid_result),
]