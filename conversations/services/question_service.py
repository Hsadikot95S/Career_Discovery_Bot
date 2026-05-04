from conversations.models import Question
from conversations.constants import ConversationStates


STATE_TO_CATEGORY = {
    ConversationStates.PROFILE: "PROFILE",
    ConversationStates.INTEREST: "INTEREST",
    ConversationStates.DEPTH: "DEPTH",
    ConversationStates.VALIDATION: "VALIDATION",
}


def get_question_for_state(state):
    category = STATE_TO_CATEGORY.get(state.current_step)

    if not category:
        return "Let's begin. Tell me about yourself."

    question = Question.objects.filter(
        category=category,
        is_active=True
    ).order_by("order").first()

    return question.text if question else "Tell me more about yourself."