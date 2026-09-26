"""
Phase 7 — Duplicate Detector Service (v2)
Combines semantic similarity, taxonomy signals, secondary domain overlap, geographic location,
and problem fingerprints into a transparent normalized composite score.

KEY DESIGN PRINCIPLES:
- UNKNOWN != MISMATCH: Missing taxonomy or location metadata does NOT penalize or suppress candidate score.
- Available-Signal Normalization: Composite score = sum(available weighted contributions) / sum(weights of available signals).
- High Semantic + Location Candidate Rule: Surfaces strong candidates even when optional metadata is missing.
- Contradiction Protection: Deterministic fingerprinting prevents different issues at the same location from false-matching.
- Human Review Boundary: AI layer ONLY recommends candidates. Automatic merges are strictly prohibited.
"""

from typing import Any, Dict, List, Optional
from app.config import settings
from app.services.embedding import EmbeddingService
from app.services.similarity import SimilarityService
from app.services.location import LocationService
from app.services.problem_fingerprint import ProblemFingerprintService


class DuplicateDetector:
    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        similarity_service: Optional[SimilarityService] = None,
        location_service: Optional[LocationService] = None,
        fingerprint_service: Optional[ProblemFingerprintService] = None,
        similarity_threshold: Optional[float] = None,
        strong_candidate_threshold: Optional[float] = None,
        semantic_strong_threshold: Optional[float] = None,
        semantic_candidate_threshold: Optional[float] = None,
        semantic_weight: Optional[float] = None,
        primary_domain_weight: Optional[float] = None,
        subcategory_weight: Optional[float] = None,
        secondary_domain_weight: Optional[float] = None,
        location_weight: Optional[float] = None,
        max_location_radius_km: Optional[float] = None,
    ):
        self.embedding_service = embedding_service or EmbeddingService(model_name=settings.EMBEDDING_MODEL)
        self.similarity_service = similarity_service or SimilarityService()
        self.location_service = location_service or LocationService()
        self.fingerprint_service = fingerprint_service or ProblemFingerprintService()

        # Thresholds
        self.similarity_threshold = (
            similarity_threshold if similarity_threshold is not None else settings.DUPLICATE_SIMILARITY_THRESHOLD
        )
        self.strong_candidate_threshold = (
            strong_candidate_threshold
            if strong_candidate_threshold is not None
            else getattr(settings, "STRONG_CANDIDATE_THRESHOLD", 0.85)
        )
        self.semantic_strong_threshold = (
            semantic_strong_threshold
            if semantic_strong_threshold is not None
            else getattr(settings, "SEMANTIC_STRONG_THRESHOLD", 0.82)
        )
        self.semantic_candidate_threshold = (
            semantic_candidate_threshold
            if semantic_candidate_threshold is not None
            else getattr(settings, "SEMANTIC_CANDIDATE_THRESHOLD", 0.70)
        )

        # Base Weights (Sum to 1.0 for full signal availability)
        self.semantic_weight = semantic_weight if semantic_weight is not None else settings.SEMANTIC_WEIGHT
        self.primary_domain_weight = (
            primary_domain_weight if primary_domain_weight is not None else settings.PRIMARY_DOMAIN_WEIGHT
        )
        self.subcategory_weight = (
            subcategory_weight if subcategory_weight is not None else settings.SUBCATEGORY_WEIGHT
        )
        self.secondary_domain_weight = (
            secondary_domain_weight if secondary_domain_weight is not None else settings.SECONDARY_DOMAIN_WEIGHT
        )
        self.location_weight = location_weight if location_weight is not None else settings.LOCATION_WEIGHT
        self.max_location_radius_km = (
            max_location_radius_km if max_location_radius_km is not None else settings.LOCATION_DISTANCE_THRESHOLD_KM
        )

        self.scoring_version = getattr(settings, "SCORING_VERSION", "duplicate-v2")

    @staticmethod
    def _calculate_jaccard_overlap(list_a: Optional[List[str]], list_b: Optional[List[str]]) -> float:
        """Calculates Jaccard similarity index between two lists of strings."""
        if not list_a or not list_b:
            return 0.0
        set_a = {s.strip().lower() for s in list_a if isinstance(s, str) and s.strip()}
        set_b = {s.strip().lower() for s in list_b if isinstance(s, str) and s.strip()}
        if not set_a or not set_b:
            return 0.0
        intersection = set_a.intersection(set_b)
        union = set_a.union(set_b)
        return round(len(intersection) / len(union), 4)

    def analyze_candidate_pair(
        self,
        problem: Dict[str, Any],
        candidate: Dict[str, Any],
        problem_embedding: Optional[List[float]] = None,
        candidate_embedding: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """
        Analyzes a single pair of new problem vs candidate problem across all signals.
        Uses Available-Signal Normalized Scoring, distinct UNKNOWN signal states, and transparent breakdown.
        """
        cand_id = candidate.get("problemId") or candidate.get("problem_id") or "UNKNOWN"

        title_a = str(problem.get("title") or "").strip()
        desc_a = str(problem.get("description") or "").strip()
        title_b = str(candidate.get("title") or "").strip()
        desc_b = str(candidate.get("description") or "").strip()

        # 1. Semantic Embedding & Cosine Similarity (Always AVAILABLE)
        text_a = f"{title_a}. {desc_a}".strip()
        text_b = f"{title_b}. {desc_b}".strip()

        if problem_embedding is None:
            problem_embedding = self.embedding_service.embed(text_a)
        if candidate_embedding is None:
            candidate_embedding = self.embedding_service.embed(text_b)

        semantic_sim = self.similarity_service.cosine_similarity(problem_embedding, candidate_embedding)

        # 2. Structured Taxonomy Signals (MATCH, MISMATCH, UNKNOWN)
        prim_a = problem.get("primaryDomain")
        prim_b = candidate.get("primaryDomain")
        has_prim_a = bool(prim_a and str(prim_a).strip())
        has_prim_b = bool(prim_b and str(prim_b).strip())

        if not has_prim_a or not has_prim_b:
            prim_state = "UNKNOWN"
            prim_match_bool = False
            prim_raw = None
            prim_used = False
            prim_contrib = None
        elif str(prim_a).strip().lower() == str(prim_b).strip().lower():
            prim_state = "MATCH"
            prim_match_bool = True
            prim_raw = 1.0
            prim_used = True
            prim_contrib = 1.0 * self.primary_domain_weight
        else:
            prim_state = "MISMATCH"
            prim_match_bool = False
            prim_raw = 0.0
            prim_used = True
            prim_contrib = 0.0

        sub_a = problem.get("subcategory")
        sub_b = candidate.get("subcategory")
        has_sub_a = bool(sub_a and str(sub_a).strip())
        has_sub_b = bool(sub_b and str(sub_b).strip())

        if not has_sub_a or not has_sub_b:
            sub_state = "UNKNOWN"
            sub_match_bool = False
            sub_raw = None
            sub_used = False
            sub_contrib = None
        elif str(sub_a).strip().lower() == str(sub_b).strip().lower():
            sub_state = "MATCH"
            sub_match_bool = True
            sub_raw = 1.0
            sub_used = True
            sub_contrib = 1.0 * self.subcategory_weight
        else:
            sub_state = "MISMATCH"
            sub_match_bool = False
            sub_raw = 0.0
            sub_used = True
            sub_contrib = 0.0

        sec_a = problem.get("secondaryDomains") or []
        sec_b = candidate.get("secondaryDomains") or []
        has_sec_a = bool(sec_a and any(isinstance(s, str) and s.strip() for s in sec_a))
        has_sec_b = bool(sec_b and any(isinstance(s, str) and s.strip() for s in sec_b))

        if not has_sec_a or not has_sec_b:
            sec_state = "UNKNOWN"
            sec_overlap = 0.0
            sec_raw = None
            sec_used = False
            sec_contrib = None
        else:
            sec_overlap = self._calculate_jaccard_overlap(sec_a, sec_b)
            sec_state = "MATCH" if sec_overlap > 0 else "MISMATCH"
            sec_raw = sec_overlap
            sec_used = True
            sec_contrib = sec_overlap * self.secondary_domain_weight

        # 3. Location Signal (AVAILABLE or UNAVAILABLE)
        loc_a = problem.get("location") or {}
        loc_b = candidate.get("location") or {}

        lat1 = loc_a.get("lat") if loc_a.get("lat") is not None else loc_a.get("latitude")
        long1 = loc_a.get("long") if loc_a.get("long") is not None else loc_a.get("longitude")
        lat2 = loc_b.get("lat") if loc_b.get("lat") is not None else loc_b.get("latitude")
        long2 = loc_b.get("long") if loc_b.get("long") is not None else loc_b.get("longitude")

        distance_km = self.location_service.haversine_distance(lat1, long1, lat2, long2)

        if distance_km is None:
            loc_state = "UNAVAILABLE"
            loc_score = 0.0
            loc_raw = None
            loc_used = False
            loc_contrib = None
        else:
            loc_state = "AVAILABLE"
            loc_score = self.location_service.calculate_location_score(
                distance_km, max_radius_km=self.max_location_radius_km
            )
            loc_raw = loc_score
            loc_used = True
            loc_contrib = loc_score * self.location_weight

        # 4. Semantic Signal (Always AVAILABLE)
        sem_state = "AVAILABLE"
        sem_raw = semantic_sim
        sem_used = True
        sem_contrib = semantic_sim * self.semantic_weight

        # 5. Normalized Composite Score Calculation
        available_weight = self.semantic_weight  # Semantic is always available
        total_contribution = sem_contrib

        if prim_used:
            available_weight += self.primary_domain_weight
            total_contribution += prim_contrib
        if sub_used:
            available_weight += self.subcategory_weight
            total_contribution += sub_contrib
        if sec_used:
            available_weight += self.secondary_domain_weight
            total_contribution += sec_contrib
        if loc_used:
            available_weight += self.location_weight
            total_contribution += loc_contrib

        available_weight = round(float(available_weight), 4)
        normalized_score = (
            round(float(total_contribution / available_weight), 4) if available_weight > 0 else 0.0
        )
        # Ensure score stays in [0.0, 1.0]
        normalized_score = max(0.0, min(1.0, normalized_score))

        # 6. Problem Fingerprinting & Contradiction Protection
        fp_a = self.fingerprint_service.extract_fingerprint(title_a, desc_a)
        fp_b = self.fingerprint_service.extract_fingerprint(title_b, desc_b)
        fp_state, is_contradictory, fp_reason = self.fingerprint_service.compare_fingerprints(fp_a, fp_b)

        # 7. Candidate Decision Rules
        semantic_strong_signal = semantic_sim >= self.semantic_strong_threshold
        location_support = (loc_state == "AVAILABLE" and loc_score >= 0.80) or (
            distance_km is not None and distance_km <= 1.0
        )
        high_semantic_location_pass = (
            semantic_strong_signal and location_support and not is_contradictory
        )

        if (normalized_score >= self.strong_candidate_threshold or high_semantic_location_pass) and not is_contradictory:
            status = "strong_candidate"
        elif normalized_score >= self.similarity_threshold and not is_contradictory:
            status = "potential_duplicate"
        else:
            status = "no_candidate"

        # 8. Explainable Reasons List (Positive, Unknown, Negative)
        reasons = []

        # Positives
        if semantic_sim >= 0.80:
            reasons.append(f"High semantic similarity ({semantic_sim:.3f})")
        elif semantic_sim >= 0.65:
            reasons.append(f"Moderate semantic similarity ({semantic_sim:.3f})")

        if prim_state == "MATCH":
            reasons.append(f"Same primary domain ({prim_a})")
        if sub_state == "MATCH":
            reasons.append(f"Same subcategory ({sub_a})")
        if sec_state == "MATCH":
            reasons.append(f"Secondary domain overlap ({sec_overlap * 100:.0f}%)")

        if loc_state == "AVAILABLE":
            if distance_km <= 1.0:
                reasons.append(f"Geographically very close ({distance_km:.2f} km)")
            elif distance_km <= self.max_location_radius_km:
                reasons.append(f"Geographically nearby ({distance_km:.2f} km)")
            else:
                reasons.append(f"Geographically distant ({distance_km:.1f} km)")

        if high_semantic_location_pass and (prim_state == "UNKNOWN" or sub_state == "UNKNOWN"):
            reasons.append("Surfaced via strong semantic similarity and close location despite missing taxonomy")

        # Unknowns
        if prim_state == "UNKNOWN":
            reasons.append("Primary domain not provided")
        if sub_state == "UNKNOWN":
            reasons.append("Subcategory not provided")
        if sec_state == "UNKNOWN":
            reasons.append("Secondary domains not provided")
        if loc_state == "UNAVAILABLE":
            reasons.append("Location coordinates missing or incomplete")

        # Negatives
        if prim_state == "MISMATCH":
            reasons.append(f"Different primary domains ({prim_a} vs {prim_b})")
        if sub_state == "MISMATCH":
            reasons.append(f"Different subcategories ({sub_a} vs {sub_b})")
        if sec_state == "MISMATCH":
            reasons.append("No secondary domain overlap")
        if semantic_sim < 0.60:
            reasons.append(f"Low semantic similarity ({semantic_sim:.3f})")
        if is_contradictory and fp_reason:
            reasons.append(f"Contradictory problem fingerprint: {fp_reason}")

        # 9. Structure Response Objects for API Transparency
        score_breakdown = {
            "semantic": {
                "rawValue": sem_raw,
                "state": sem_state,
                "weight": self.semantic_weight,
                "contribution": round(sem_contrib, 4),
                "used": sem_used,
            },
            "primaryDomain": {
                "rawValue": prim_raw,
                "state": prim_state,
                "weight": self.primary_domain_weight,
                "contribution": round(prim_contrib, 4) if prim_contrib is not None else None,
                "used": prim_used,
            },
            "subcategory": {
                "rawValue": sub_raw,
                "state": sub_state,
                "weight": self.subcategory_weight,
                "contribution": round(sub_contrib, 4) if sub_contrib is not None else None,
                "used": sub_used,
            },
            "secondaryDomains": {
                "rawValue": sec_raw,
                "state": sec_state,
                "weight": self.secondary_domain_weight,
                "contribution": round(sec_contrib, 4) if sec_contrib is not None else None,
                "used": sec_used,
            },
            "location": {
                "rawValue": loc_raw,
                "state": loc_state,
                "weight": self.location_weight,
                "contribution": round(loc_contrib, 4) if loc_contrib is not None else None,
                "used": loc_used,
            },
        }

        weights_dict = {
            "semantic": self.semantic_weight,
            "primaryDomain": self.primary_domain_weight,
            "subcategory": self.subcategory_weight,
            "secondaryDomain": self.secondary_domain_weight,
            "location": self.location_weight,
        }

        weighted_contributions = {
            "semantic": round(sem_contrib, 4),
            "primaryDomain": round(prim_contrib, 4) if prim_contrib is not None else None,
            "subcategory": round(sub_contrib, 4) if sub_contrib is not None else None,
            "secondaryDomain": round(sec_contrib, 4) if sec_contrib is not None else None,
            "location": round(loc_contrib, 4) if loc_contrib is not None else None,
        }

        signal_states = {
            "primaryDomain": prim_state,
            "subcategory": sub_state,
            "secondaryDomains": sec_state,
            "location": loc_state,
            "fingerprint": fp_state,
        }

        decision_evidence = {
            "thresholdUsed": self.similarity_threshold,
            "strongCandidateThreshold": self.strong_candidate_threshold,
            "semanticStrongSignal": semantic_strong_signal,
            "locationSupport": location_support,
            "contradictorySignals": is_contradictory,
            "highSemanticLocationPass": high_semantic_location_pass,
        }

        return {
            "candidateProblemId": cand_id,
            "duplicateScore": normalized_score,
            "semanticSimilarity": semantic_sim,
            "primaryDomainMatch": prim_match_bool,
            "subcategoryMatch": sub_match_bool,
            "secondaryDomainOverlap": sec_overlap,
            "locationDistanceKm": distance_km,
            "locationScore": loc_score,
            "candidateStatus": status,
            "reasons": reasons,
            "signalStates": signal_states,
            "scoreBreakdown": score_breakdown,
            "weights": weights_dict,
            "weightedContributions": weighted_contributions,
            "availableWeight": available_weight,
            "normalizedCompositeScore": normalized_score,
            "decisionEvidence": decision_evidence,
            "fingerprint": {
                "fp_a": fp_a,
                "fp_b": fp_b,
                "state": fp_state,
                "isContradictory": is_contradictory,
                "reason": fp_reason,
            },
            "scoringVersion": self.scoring_version,
        }

    def detect_duplicates(
        self,
        problem: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        top_k: int = 10,
    ) -> Dict[str, Any]:
        """
        Processes a new problem against a list of candidate problems, returning ranked recommendations.
        """
        prob_id = problem.get("problemId") or problem.get("problem_id") or "NEW_PROBLEM"

        if not candidates:
            return {
                "problemId": prob_id,
                "status": "no_candidate",
                "duplicateCandidates": [],
                "scoringVersion": self.scoring_version,
            }

        text_a = f"{problem.get('title', '')}. {problem.get('description', '')}".strip()
        prob_emb = self.embedding_service.embed(text_a)

        results = []
        for cand in candidates:
            analysis = self.analyze_candidate_pair(
                problem=problem, candidate=cand, problem_embedding=prob_emb
            )
            results.append(analysis)

        # Rank descending by duplicate score
        results.sort(key=lambda x: x["duplicateScore"], reverse=True)
        top_results = results[:top_k]

        has_candidate = any(
            r["candidateStatus"] in ("strong_candidate", "potential_duplicate") for r in top_results
        )
        overall_status = "candidate_found" if has_candidate else "no_candidate"

        return {
            "problemId": prob_id,
            "status": overall_status,
            "duplicateCandidates": top_results,
            "scoringVersion": self.scoring_version,
        }
