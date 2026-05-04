from conversations.models import Question

def seed_questions():
    questions = [
        (1, "What subjects do you enjoy the most?", "PROFILE"),
        (2, "Tell me about your academic background", "PROFILE"),

        (3, "Do you prefer problem-solving or creativity?", "INTEREST"),
        (4, "What kind of activities excite you?", "INTEREST"),

        (5, "Do you enjoy working on complex technical problems?", "DEPTH"),
        (6, "Do you like research or practical work?", "DEPTH"),

        (7, "Would you prefer a stable career or dynamic one?", "VALIDATION"),
        (8, "Do you enjoy working independently or in teams?", "VALIDATION"),
    ]

    for order, text, category in questions:
        Question.objects.update_or_create(
            order=order,
            defaults={
                "text": text,
                "category": category,
                "is_active": True,
            }
        )

    print("✅ Questions seeded successfully")