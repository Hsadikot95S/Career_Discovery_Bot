from django.http import JsonResponse
from user_sessions.models import Session

from matching.rag_engine import get_top_careers
from matching.utils import build_user_profile
from matching.llm_engine import generate_explanation
from matching.hybrid_engine import hybrid_recommendation


def basic_recommendation(request, session_id):
    """
    RAG-only recommendations (no scoring)
    """
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return JsonResponse({"error": "Invalid session"}, status=404)

    user_profile = build_user_profile(session)
    careers = get_top_careers(user_profile["raw_text"])

    return JsonResponse({
        "query": user_profile,
        "recommendations": careers
    })


def scored_recommendation(request, session_id):
    """
    Hybrid scoring (features + RAG + signals)
    """
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return JsonResponse({"error": "Invalid session"}, status=404)

    result = hybrid_recommendation(session)

    return JsonResponse(result)


def final_recommendation(request, session_id):
    """
    Final output (LLM explanation on top of recommendations)
    """
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return JsonResponse({"error": "Invalid session"}, status=404)

    user_profile = build_user_profile(session)
    careers = get_top_careers(user_profile["raw_text"])

    result = generate_explanation(user_profile, careers)

    return JsonResponse(result)