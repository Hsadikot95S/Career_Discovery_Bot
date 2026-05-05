def extract_features(text):
    text = text.lower()

    technical = 0
    creativity = 0
    analytical = 0
    business = 0
    research = 0

    # TECHNICAL
    if any(word in text for word in ["coding", "programming", "algorithms"]):
        technical += 2

    # ANALYTICAL
    if any(word in text for word in ["math", "analysis", "problem solving"]):
        analytical += 2

    # BUSINESS
    if any(word in text for word in ["business", "marketing", "sales"]):
        business += 2

    # RESEARCH
    if any(word in text for word in ["research", "experiment", "study"]):
        research += 2

    # NEW FIX (IMPORTANT)
    if any(word in text for word in [
        "writing", "literature", "storytelling",
        "hindi", "english", "language", "poetry"
    ]):
        creativity += 3

    # NEGATIVE SIGNAL
    if "coding" in text and ("not" in text or "dont" in text):
        technical = max(0, technical - 2)

    return {
        "technical": technical,
        "creativity": creativity,
        "analytical": analytical,
        "business": business,
        "research": research,
    }