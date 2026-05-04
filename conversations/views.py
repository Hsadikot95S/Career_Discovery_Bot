from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question, ConversationState, Message
from user_sessions.models import Session
from features.extractor import extract_features
from features.models import FeatureVector
import json



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
def next_question(request, session_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        data = json.loads(request.body)
        user_answer = data.get("answer")

        if not user_answer:
            return JsonResponse({"error": "Answer required"}, status=400)

        session = Session.objects.get(id=session_id)
        state = session.state  # using related_name

    except Session.DoesNotExist:
        return JsonResponse({"error": "Invalid session"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

    Message.objects.create(
        session=session,
        role="user",
        content=user_answer
    )

    
    features = extract_features(user_answer)

    FeatureVector.objects.create(
        session=session,
        source_text=user_answer,
        **features
    )

    next_q = Question.objects.filter(
        order__gt=state.step_index,
        is_active=True
    ).order_by("order").first()

    if not next_q:
        state.is_completed = True
        state.save()

        return JsonResponse({
            "message": "Conversation complete"
        })

    state.step_index = next_q.order
    state.save()

    
    Message.objects.create(
        session=session,
        role="assistant",
        content=next_q.text
    )

    return JsonResponse({
        "next_question": next_q.text,
        "step_index": state.step_index
    })