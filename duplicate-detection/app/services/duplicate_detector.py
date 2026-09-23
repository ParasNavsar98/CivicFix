"""
Phase 7 — Duplicate Detector Service
Combines semantic similarity, taxonomy matching, secondary domain overlap, and geographic location into a transparent composite score.

SRS REQUIREMENT COMPLIANCE:
- AI surfaces candidate recommendations and evidence/signals.
- AI DOES NOT automatically merge, delete, or replace problem records.
- Human reviewer retains 100% control over consequential merge decisions.
"""

from typing import Any, Dict, List, Optional
from app.config import settings
from app.services.embedding import EmbeddingService
from app.services.similarity import SimilarityService
from app.services.location import LocationService


class DuplicateDetector:
    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        similarity_service: Optional[SimilarityService] = None,
        location_service: Optional[LocationService] = None,
        similarity_threshold: Optional[float] = None,
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

        # Configurable parameters
        self.similarity_threshold = (
            similarity_threshold if similarity_threshold is not None else settings.DUPLICATE_SIMILARITY_THRESHOLD
        )
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
        Returns detailed scoring breakdown, status recommendation, and explicit reasons list.
        """
        cand_id = candidate.get("problemId") or candidate.get("problem_id") or "UNKNOWN"

        # 1. Semantic Embedding & Cosine Similarity
        text_a = f"{problem.get('title', '')}. {problem.get('description', '')}".strip()
        text_b = f"{candidate.get('title', '')}. {candidate.get('description', '')}".strip()

        if problem_embedding is None:
            problem_embedding = self.embedding_service.embed(text_a)
        if candidate_embedding is None:
            candidate_embedding = self.embedding_service.embed(text_b)

        semantic_sim = self.similarity_service.cosine_similarity(problem_embedding, candidate_embedding)

        # 2. Structured Taxonomy Signals
        prim_a = problem.get("primaryDomain")
        prim_b = candidate.get("primaryDomain")
        primary_domain_match = (
            bool(prim_a and prim_b and str(prim_a).strip().lower() == str(prim_b).strip().lower())
        )

        sub_a = problem.get("subcategory")
        sub_b = candidate.get("subcategory")
        subcategory_match = (
            bool(sub_a and sub_b and str(sub_a).strip().lower() == str(sub_b).strip().lower())
        )

        sec_a = problem.get("secondaryDomains") or []
        sec_b = candidate.get("secondaryDomains") or []
        sec_overlap = self._calculate_jaccard_overlap(sec_a, sec_b)

        # 3. Location Signal
        loc_a = problem.get("location") or {}
        loc_b = candidate.get("location") or {}

        lat1 = loc_a.get("lat") or loc_a.get("latitude")
        long1 = loc_a.get("long") or loc_a.get("longitude")
        lat2 = loc_b.get("lat") or loc_b.get("latitude")
        long2 = loc_b.get("long") or loc_b.get("longitude")

        distance_km = self.location_service.haversine_distance(lat1, long1, lat2, long2)
        location_score = self.location_service.calculate_location_score(
            distance_km, max_radius_km=self.max_location_radius_km
        )

        # 4. Multi-Factor Composite Score Calculation
        composite_score = (
            (semantic_sim * self.semantic_weight)
            + ((1.0 if primary_domain_match else 0.0) * self.primary_domain_weight)
            + ((1.0 if subcategory_match else 0.0) * self.subcategory_weight)
            + (sec_overlap * self.secondary_domain_weight)
            + (location_score * self.location_weight)
        )
        composite_score = round(float(composite_score), 4)

        # 5. Status Determination
        if composite_score >= 0.85:
            status = "strong_candidate"
        elif composite_score >= self.similarity_threshold:
            status = "potential_duplicate"
        else:
            status = "no_candidate"

        # 6. Human-Readable Explainability Reasons
        reasons = []
        if semantic_sim >= 0.80:
            reasons.append(f"High semantic similarity ({semantic_sim:.3f})")
        elif semantic_sim >= 0.65:
            reasons.append(f"Moderate semantic similarity ({semantic_sim:.3f})")

        if primary_domain_match:
            reasons.append(f"Same primary domain ({prim_a})")

        if subcategory_match:
            reasons.append(f"Same subcategory ({sub_a})")

        if sec_overlap > 0:
            reasons.append(f"Secondary domain overlap ({sec_overlap * 100:.0f}%)")

        if distance_km is not None:
            if distance_km <= 1.0:
                reasons.append(f"Geographically very close ({distance_km:.2f} km)")
            elif distance_km <= self.max_location_radius_km:
                reasons.append(f"Geographically nearby ({distance_km:.2f} km)")
            else:
                reasons.append(f"Geographically distant ({distance_km:.1f} km)")
        else:
            reasons.append("Location coordinates missing or incomplete")

        if not reasons:
            reasons.append("Low overall similarity across all features")

        return {
            "candidateProblemId": cand_id,
            "duplicateScore": composite_score,
            "semanticSimilarity": semantic_sim,
            "primaryDomainMatch": primary_domain_match,
            "subcategoryMatch": subcategory_match,
            "secondaryDomainOverlap": sec_overlap,
            "locationDistanceKm": distance_km,
            "locationScore": location_score,
            "candidateStatus": status,
            "reasons": reasons,
        }

    def detect_duplicates(
        self,
        problem: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        top_k: int = 10,
    ) -> Dict[str, Any]:
        """
        Processes a new problem against a list of candidates, returns ranked candidate recommendations.
        """
        prob_id = problem.get("problemId") or problem.get("problem_id") or "NEW_PROBLEM"

        if not candidates:
            return {
                "problemId": prob_id,
                "status": "no_candidate",
                "duplicateCandidates": [],
            }

        # Embed query problem once
        text_a = f"{problem.get('title', '')}. {problem.get('description', '')}".strip()
        prob_emb = self.embedding_service.embed(text_a)

        results = []
        for cand in candidates:
            analysis = self.analyze_candidate_pair(
                problem=problem, candidate=cand, problem_embedding=prob_emb
            )
            # Filter candidates below minimum threshold or include all for ranking
            results.append(analysis)

        # Rank descending by duplicate score
        results.sort(key=lambda x: x["duplicateScore"], reverse=True)
        top_results = results[:top_k]

        has_strong = any(r["candidateStatus"] in ("strong_candidate", "potential_duplicate") for r in top_results)
        overall_status = "candidate_found" if has_strong else "no_candidate"

        return {
            "problemId": prob_id,
            "status": overall_status,
            "duplicateCandidates": top_results,
        }
