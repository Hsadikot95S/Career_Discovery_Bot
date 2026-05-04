from conversations.models import Message


def build_user_profile(session):
    messages = Message.objects.filter(session=session, role="user")

    combined_text = " ".join([m.content for m in messages])

    return combined_text