from features.models import FeatureVector


# 🔹 STEP 1 — Aggregate all feature vectors
def aggregate_features(session):
    vectors = FeatureVector.objects.filter(session=session)

    aggregate = {
        "technical": 0.0,
        "creativity": 0.0,
        "analytical": 0.0,
        "business": 0.0,
        "research": 0.0,
    }

    if not vectors.exists():
        return aggregate  # empty fallback

    for v in vectors:
        aggregate["technical"] += v.technical
        aggregate["creativity"] += v.creativity
        aggregate["analytical"] += v.analytical
        aggregate["business"] += v.business
        aggregate["research"] += v.research

    return aggregate


# 🔹 STEP 2 — Normalize features (important for stability)
def normalize_features(features):
    total = sum(features.values())

    if total == 0:
        return features  # avoid division by zero

    return {k: v / total for k, v in features.items()}


# 🔹 STEP 3 — Compute domain scores
def compute_domain_scores(features):
    features = normalize_features(features)

    scores = {
        "Engineering": (
            features["technical"] * 2.0 +
            features["analytical"] * 1.5
        ),

        "Design": (
            features["creativity"] * 2.0
        ),

        "Business": (
            features["business"] * 2.0 +
            features["creativity"] * 0.5
        ),

        "Research": (
            features["research"] * 2.0 +
            features["analytical"] * 1.0
        ),
    }

    return scores


# 🔹 STEP 4 — Rank domains
def rank_domains(scores):
    return sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )


# 🔹 STEP 5 — Full pipeline (important abstraction)
def generate_recommendation(session):
    features = aggregate_features(session)
    scores = compute_domain_scores(features)
    ranked = rank_domains(scores)

    return {
        "features": features,
        "scores": scores,
        "recommendations": ranked[:3]  # top 3
    }