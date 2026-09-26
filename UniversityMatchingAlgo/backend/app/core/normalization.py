"""
Deterministic, explainable term normalization.

Used by every scoring factor that compares free-text terms (expertise,
resources, domains, etc). NO LLM. NO fuzzy ML matching. Just:
  lowercase -> trim -> strip punctuation -> collapse whitespace -> synonym map

This keeps every match traceable: we can always say exactly why two terms
were (or weren't) considered equivalent.
"""
import re

# Config-driven synonym groups. Each inner list is a set of terms considered
# equivalent. Extend this without touching any scoring logic.
# In production this can be loaded from `matching_configuration` in Mongo;
# this hardcoded default is the fallback / seed value.
DEFAULT_SYNONYM_GROUPS: list[list[str]] = [
    ["environmental management", "env management", "environment management"],
    ["public health", "health", "community health"],
    ["waste management", "solid waste management", "garbage management"],
    ["pollution control", "pollution management"],
    ["environmental engineering", "env engineering"],
    ["civil engineering", "structural engineering"],
    ["computer science", "computer science and engineering", "cse"],
    ["iot", "internet of things", "iot monitoring"],
    ["data analysis", "data analytics", "data science"],
    ["waste collection", "garbage collection"],
    ["waste disposal infrastructure", "waste disposal", "disposal infrastructure"],
]


def _clean(term: str) -> str:
    term = term.lower().strip()
    term = re.sub(r"[^\w\s]", "", term)  # strip punctuation
    term = re.sub(r"\s+", " ", term)  # collapse whitespace
    return term


def build_synonym_lookup(
    synonym_groups: list[list[str]] | None = None,
) -> dict[str, str]:
    """
    Returns a dict mapping every cleaned synonym -> a canonical cleaned term
    (the first item in its group). Terms not in any group map to themselves.
    """
    groups = synonym_groups if synonym_groups is not None else DEFAULT_SYNONYM_GROUPS
    lookup: dict[str, str] = {}
    for group in groups:
        cleaned_group = [_clean(t) for t in group]
        canonical = cleaned_group[0]
        for term in cleaned_group:
            lookup[term] = canonical
    return lookup


def normalize_term(term: str, synonym_lookup: dict[str, str] | None = None) -> str:
    """Normalize a single term to its canonical form."""
    cleaned = _clean(term)
    lookup = synonym_lookup if synonym_lookup is not None else build_synonym_lookup()
    return lookup.get(cleaned, cleaned)


def normalize_terms(
    terms: list[str], synonym_lookup: dict[str, str] | None = None
) -> set[str]:
    """Normalize a list of terms into a set of canonical forms."""
    lookup = synonym_lookup if synonym_lookup is not None else build_synonym_lookup()
    return {normalize_term(t, lookup) for t in terms if t and t.strip()}


def match_terms(
    required: list[str],
    available: list[str],
    synonym_lookup: dict[str, str] | None = None,
) -> tuple[set[str], set[str]]:
    """
    Compare a required-terms list against an available-terms list.

    Returns (matched_required_terms_original_casing, unmatched_required_terms_original_casing)
    Matching is done on normalized forms, but returned sets use the ORIGINAL
    casing of the `required` list so explanations stay human-readable.
    """
    lookup = synonym_lookup if synonym_lookup is not None else build_synonym_lookup()
    available_normalized = normalize_terms(available, lookup)

    matched: set[str] = set()
    unmatched: set[str] = set()
    for term in required:
        if not term or not term.strip():
            continue
        norm = normalize_term(term, lookup)
        if norm in available_normalized:
            matched.add(term)
        else:
            unmatched.add(term)
    return matched, unmatched
