from conversations.models import ConversationState
from conversations.services.state_service import get_next_step


def initialize_state(session):
    state, created = ConversationState.objects.get_or_create(session=session)
    return state


def advance_state(state: ConversationState):
    next_step = get_next_step(state.current_step)

    state.current_step = next_step
    state.step_index += 1

    if next_step == "END":
        state.is_completed = True

    state.save()
    return state