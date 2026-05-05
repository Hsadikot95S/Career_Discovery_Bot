from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question, ConversationState, Message
from user_sessions.models import Session
from features.extractor import extract_features
from features.models import FeatureVector
import json
from features.extractor import extract_features
from features.models import FeatureVector
from conversations.models import Message

@csrf_exempt
def start_conversation(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    session = Session.objects.create()

    first_q = Question.objects.filter(is_active=True).order_by("order").first()

    if not first_q:
        return JsonResponse({"error": "No questions found"}, status=500)

    state = ConversationState.objects.create(
        session=session,
        step_index=first_q.order,
        current_step="START"
    )

    Message.objects.create(
        session=session,
        role="assistant",
        content=first_q.text
    )

    return JsonResponse({
        "session_id": str(session.id),
        "question": first_q.text
    })

@csrf_exempt
def answer_question(request):
    if request.method == "POST":
        data = json.loads(request.body)

        session_id = data.get("session_id")
        answer = data.get("answer")

        session = Session.objects.get(id=session_id)
        state = ConversationState.objects.get(session=session)

        # Simple flow logic
        next_step_map = {
            "PROFILE": "INTEREST",
            "INTEREST": "DEPTH",
            "DEPTH": "VALIDATION",
            "VALIDATION": "COMPLETE"
        }

        current_step = state.current_step
        next_step = next_step_map.get(current_step)

        if next_step == "COMPLETE":
            return JsonResponse({
                "message": "Conversation complete"
            })

        # update state
        state.current_step = next_step
        state.save()

        # fetch next question
        question = Question.objects.filter(
            category=next_step,
            is_active=True
        ).order_by("order").first()

        return JsonResponse({
            "next_step": next_step,
            "question": question.text
        })
    
@csrf_exempt



def respond(request, session_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    # 1. Get session
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return JsonResponse({"error": "Invalid session"}, status=404)

    # 2. Parse request safely
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # 3. Extract answer safely
    answer = data.get("answer")
    if not answer:
        return JsonResponse({"error": "Answer required"}, status=400)

    # 4. Save message (CRITICAL)
    Message.objects.create(
        session=session,
        role="user",
        content=answer,
        input_type="text"
    )

    # 5. Extract features
    features = extract_features(answer)

    # 6. Save features
    FeatureVector.objects.create(
        session=session,
        technical=features["technical"],
        creativity=features["creativity"],
        analytical=features["analytical"],
        business=features["business"],
        research=features["research"],
    )

    return JsonResponse({
        "message": "Answer saved",
        "features": features
    })