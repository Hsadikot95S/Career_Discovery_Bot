from matching.engine import aggregate_features, compute_domain_scores
from matching.rag_engine import get_top_careers


# Weight config (tunable)
RAG_WEIGHT = 0.6
DOMAIN_WEIGHT = 0.4


def hybrid_recommendation(session):
    # 1. Feature → domain scores
    features = aggregate_features(session)
    domain_scores = compute_domain_scores(features)

    # 2. RAG results
    user_profile = " ".join(
        [m.content for m in session.messages.filter(role="user")]
    )

    rag_results = get_top_careers(user_profile)

    final_scores = []

    for i, career in enumerate(rag_results):
        domain = career.get("domain", "")

        # RAG score (rank-based)
        rag_score = 1 / (i + 1)  # rank 1 = 1.0, rank 2 = 0.5

        # Domain score
        domain_score = domain_scores.get(domain, 0)

        # Combine
        final_score = (
            rag_score * RAG_WEIGHT +
            domain_score * DOMAIN_WEIGHT
        )

        final_scores.append({
            "career": career["title"],
            "score": round(final_score, 3),
            "domain": domain,
            "rag_score": rag_score,
            "domain_score": domain_score
        })

    # Sort final
    final_scores = sorted(final_scores, key=lambda x: x["score"], reverse=True)

    return {
        "features": features,
        "domain_scores": domain_scores,
        "recommendations": final_scores
    }