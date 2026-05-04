def extract_features(text: str):
    text = text.lower()

    features = {
        "technical": 0.0,
        "creativity": 0.0,
        "analytical": 0.0,
        "business": 0.0,
        "research": 0.0,
    }

    # VERY SIMPLE RULES (we improve later with ML)

    if any(word in text for word in ["math", "physics", "coding", "programming"]):
        features["technical"] += 1

    if any(word in text for word in ["design", "art", "creative"]):
        features["creativity"] += 1

    if any(word in text for word in ["analyze", "logic", "problem", "solve"]):
        features["analytical"] += 1

    if any(word in text for word in ["business", "startup", "market"]):
        features["business"] += 1

    if any(word in text for word in ["research", "study", "investigate"]):
        features["research"] += 1

    return features