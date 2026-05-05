from matching.engine import aggregate_features, compute_domain_scores
from matching.rag_engine import get_top_careers


# Tunable weights
RAG_WEIGHT = 0.5
DOMAIN_WEIGHT = 0.3
SIGNAL_WEIGHT = 0.2


def build_user_text(session):
    """
    Combine all user responses into a single normalized text blob
    """
    messages = session.messages.filter(role="user")
    text = " ".join([m.content for m in messages])
    return text.lower()


def score_signals(user_text, career):
    """
    Match user text against career signals
    """
    score = 0

    for signal in career.get("signals", []):
        if signal in user_text:
            score += 1

    return score


def hybrid_recommendation(session):
    # 1. Aggregate features → domain scores
    features = aggregate_features(session)
    domain_scores = compute_domain_scores(features)

    # 2. Build full user context (IMPORTANT FIX)
    user_text = build_user_text(session)

    # 3. RAG retrieval
    rag_results = get_top_careers(user_text)

    final_scores = []

    for i, career in enumerate(rag_results):
        domain = career.get("domain", "")

        # RAG score (rank-based)
        rag_score = 1 / (i + 1)

        # Domain score (normalized)
        domain_score = domain_scores.get(domain, 0)

        # NEW: Signal score
        signal_score = score_signals(user_text, career)

        # Normalize signal score (avoid explosion)
        signal_score = min(signal_score, 3) / 3  # scale to 0–1

        # Combine all signals
        final_score = (
            rag_score * RAG_WEIGHT +
            domain_score * DOMAIN_WEIGHT +
            signal_score * SIGNAL_WEIGHT
        )

        final_scores.append({
            "career": career["title"],
            "score": round(final_score, 3),
            "domain": domain,
            "rag_score": round(rag_score, 3),
            "domain_score": round(domain_score, 3),
            "signal_score": round(signal_score, 3)
        })

    # 4. Final ranking
    final_scores = sorted(final_scores, key=lambda x: x["score"], reverse=True)

    return {
        "features": features,
        "domain_scores": domain_scores,
        "recommendations": final_scores
    }