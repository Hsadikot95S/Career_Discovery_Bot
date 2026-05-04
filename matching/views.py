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

    # Step 1: Build profile
    user_profile = build_user_profile(session)

    # Step 2: Get RAG careers
    careers = get_top_careers(user_profile)

    # Step 3: LLM explanation
    llm_output = generate_explanation(user_profile, careers)

    try:
        parsed = json.loads(llm_output)
    except:
        return JsonResponse({
            "error": "LLM output parsing failed",
            "raw": llm_output
        })

    return JsonResponse(parsed)