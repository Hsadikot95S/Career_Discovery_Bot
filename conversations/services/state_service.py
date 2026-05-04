from conversations.constants import ConversationStates


def get_next_step(current_step):
    order = ConversationStates.ORDER
    try:
        idx = order.index(current_step)
        return order[idx + 1] if idx + 1 < len(order) else ConversationStates.END
    except ValueError:
        return ConversationStates.START