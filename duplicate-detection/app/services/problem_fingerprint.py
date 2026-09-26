"""
Problem Fingerprint Service for CivicFix Duplicate Detection.
Extracts structured problem features (entity, resource, problem type) deterministically
to detect contradictions between problems that share location or domain but refer to different issues.
"""

import re
from typing import Any, Dict, Optional, Tuple


class ProblemFingerprintService:
    # Common civic entity patterns
    ENTITY_PATTERNS = {
        "hospital": r"\b(hospital|clinic|phc|health center|dispensary|medical center)\b",
        "school": r"\b(school|classroom|college|academy|institution)\b",
        "road": r"\b(road|street|highway|lane|avenue|flyover|bridge|junction)\b",
        "water_system": r"\b(water pipe|pipeline|water supply|tap|reservoir|drain|drainage|sewer)\b",
        "lighting": r"\b(street light|streetlight|lamp|light pole)\b",
        "waste_site": r"\b(garbage|trash|waste|dump|dustbin|compactor)\b",
        "power_grid": r"\b(transformer|electricity|power line|substation|feeder)\b",
        "park": r"\b(park|garden|playground)\b",
    }

    # Common civic resource patterns
    RESOURCE_PATTERNS = {
        "medicine": r"\b(medicine|medicines|drug|drugs|vaccine|medical supplies|first aid)\b",
        "electricity": r"\b(electricity|power|voltage|current)\b",
        "water": r"\b(water|drinking water|clean water)\b",
        "light": r"\b(light|lighting|illumination)\b",
        "waste": r"\b(garbage|trash|waste|refuse|litter)\b",
        "road_surface": r"\b(pothole|potholes|crater|asphalt|tarmac|road surface)\b",
        "sewage": r"\b(sewage|drainage|wastewater|sludge)\b",
    }

    # Common problem action/failure patterns
    PROBLEM_TYPE_PATTERNS = {
        "shortage": r"\b(shortage|lacks|lack|unavailability|unavailable|deficit|depleted|scarcity)\b",
        "outage": r"\b(outage|blackout|failure|darkness|not working|cut|breakdown|tripped)\b",
        "damage": r"\b(damaged|broken|ruptured|cracked|burst|destroyed)\b",
        "leakage": r"\b(leak|leakage|burst|gushing|overflowing|flooding)\b",
        "dumping_burning": r"\b(burning|dumped|dumping|accumulation|unprocessed)\b",
        "blockage": r"\b(blockage|blocked|clogged|stagnant)\b",
        "expensive": r"\b(expensive|high cost|overcharging|overpriced)\b",
    }

    def extract_fingerprint(self, title: str, description: str) -> Dict[str, Any]:
        """
        Extracts lightweight problem fingerprint features from title and description.
        Returns extracted values and signal state (AVAILABLE or UNKNOWN).
        """
        text = f"{title} {description}".lower()

        entity = self._match_patterns(text, self.ENTITY_PATTERNS)
        resource = self._match_patterns(text, self.RESOURCE_PATTERNS)
        problem_type = self._match_patterns(text, self.PROBLEM_TYPE_PATTERNS)

        has_data = any([entity, resource, problem_type])
        state = "AVAILABLE" if has_data else "UNKNOWN"

        return {
            "state": state,
            "affectedEntity": entity,
            "affectedResource": resource,
            "problemType": problem_type,
        }

    def _match_patterns(self, text: str, pattern_dict: Dict[str, str]) -> Optional[str]:
        for key, pattern in pattern_dict.items():
            if re.search(pattern, text, re.IGNORECASE):
                return key
        return None

    def compare_fingerprints(
        self, fp_a: Dict[str, Any], fp_b: Dict[str, Any]
    ) -> Tuple[str, bool, Optional[str]]:
        """
        Compares two fingerprints.
        Returns:
            state: "MATCH", "MISMATCH", or "UNKNOWN"
            is_contradictory: bool (True if explicit contradiction detected, e.g., medicine shortage vs electricity outage)
            reason: str or None
        """
        if fp_a.get("state") == "UNKNOWN" or fp_b.get("state") == "UNKNOWN":
            return "UNKNOWN", False, None

        ent_a, ent_b = fp_a.get("affectedEntity"), fp_b.get("affectedEntity")
        res_a, res_b = fp_a.get("affectedResource"), fp_b.get("affectedResource")
        type_a, type_b = fp_a.get("problemType"), fp_b.get("problemType")

        # Explicit contradiction check: same entity (e.g. hospital), but completely different resource or problem type
        if ent_a and ent_b and ent_a == ent_b:
            if res_a and res_b and res_a != res_b:
                return (
                    "MISMATCH",
                    True,
                    f"Contradictory problem resources at same entity ({res_a} vs {res_b})",
                )
            if type_a and type_b and type_a != type_b and not (
                {type_a, type_b}.issubset({"damage", "leakage"}) or {type_a, type_b}.issubset({"shortage", "expensive"})
            ):
                return (
                    "MISMATCH",
                    True,
                    f"Contradictory problem types at same entity ({type_a} vs {type_b})",
                )

        if (res_a and res_b and res_a == res_b) and (type_a and type_b and type_a == type_b):
            return "MATCH", False, "Matching problem resource and issue type"

        if (res_a and res_b and res_a != res_b) or (type_a and type_b and type_a != type_b):
            return "MISMATCH", False, "Different problem resource or issue type"

        return "UNKNOWN", False, None
