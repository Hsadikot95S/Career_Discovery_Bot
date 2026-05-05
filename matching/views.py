from django.http import JsonResponse
from user_sessions.models import Session
from .engine import generate_recommendation
from .rag_engine import get_top_careers
from .utils import build_user_profile
from matching.llm_engine import generate_explanation
from matching.rag_engine import get_top_careers
from matching.utils import build_user_profile
from user_sessions.models import Session
from django.http import JsonResponse
import json
from matching.hybrid_engine import hybrid_recommendation


def get_recommendation(request, session_id):
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return JsonResponse({"error": "Invalid session"}, status=404)

    user_profile = build_user_profile(session)

    careers = get_top_careers(user_profile)

    return JsonResponse({
        "query": user_profile,
        "recommendations": careers
    })

def final_recommendation(request, session_id):
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return JsonResponse({"error": "Invalid session"}, status=404)

    # Step 1
    user_profile = build_user_profile(session)

    # Step 2
    careers = get_top_careers(user_profile)

    # Step 3 (LLM already returns parsed JSON)
    result = generate_explanation(user_profile, careers)

    # 🔥 DO NOT PARSE AGAIN
    return JsonResponse(result)

def hybrid_result(request, session_id):
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return JsonResponse({"error": "Invalid session"}, status=404)

    result = hybrid_recommendation(session)

    return JsonResponse(result)