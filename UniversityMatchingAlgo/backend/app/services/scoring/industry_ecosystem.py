"""
Industry Ecosystem Relevance — 5% weight.

NOTE: this is NOT industry matching. It's a small signal on whether the
university already has industry relationships broadly relevant to the
problem's domain. Config-driven domain -> keyword mapping, easily extended.
"""

DEFAULT_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "environment": ["environmental", "waste", "sustainability", "green", "climate"],
    "agriculture": ["agri", "farming", "agtech", "food"],
    "healthcare": ["health", "medical", "pharma", "biotech"],
    "infrastructure": ["construction", "civil", "infrastructure", "engineering"],
    "technology": ["technology", "software", "iot", "electronics", "ai"],
}


def score_industry_ecosystem(
    primary_domain: str, university: dict, domain_keywords: dict | None = None
) -> dict:
    relationships = university.get("industryRelationships") or []

    if not relationships:
        return {
            "score": 0.0,
            "matched_relationships": [],
            "explanation": "University has no recorded industry relationships.",
        }

    keywords_map = domain_keywords if domain_keywords is not None else DEFAULT_DOMAIN_KEYWORDS
    keywords = keywords_map.get(primary_domain.strip().lower(), [])

    matched = []
    if keywords:
        for rel in relationships:
            rel_lower = rel.lower()
            if any(kw in rel_lower for kw in keywords):
                matched.append(rel)

    if matched:
        return {
            "score": 1.0,
            "matched_relationships": matched,
            "explanation": (
                f"Industry relationships directly relevant to '{primary_domain}': "
                f"{', '.join(matched)}."
            ),
        }

    return {
        "score": 0.3,
        "matched_relationships": [],
        "explanation": (
            "University has some industry relationships, but none specifically "
            f"aligned with '{primary_domain}'."
        ),
    }
