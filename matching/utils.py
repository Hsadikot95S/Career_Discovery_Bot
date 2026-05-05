from conversations.models import Message


def build_user_profile(session):
    messages = Message.objects.filter(session=session, role="user")

    text = " ".join([m.content for m in messages])

    return {
        "raw_text": text.lower()
    }