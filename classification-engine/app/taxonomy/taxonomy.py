from typing import Dict, List

TAXONOMY: Dict[str, List[str]] = {
    "Education": [
        "Access",
        "Infrastructure",
        "Learning Support",
        "Digital Education",
    ],
    "Healthcare": [
        "Access",
        "Public Health",
        "Facilities",
        "Diagnostics",
    ],
    "Agriculture": [
        "Irrigation",
        "Crop Support",
        "Storage",
        "Market Linkage",
    ],
    "Water Resources": [
        "Supply",
        "Quality",
        "Leakage",
        "Conservation",
        "Monitoring",
    ],
    "Sanitation": [
        "Waste",
        "Drainage",
        "Toilets",
        "Cleanliness",
    ],
    "Environment": [
        "Pollution",
        "Biodiversity",
        "Waste Reduction",
        "Climate Resilience",
    ],
    "Energy": [
        "Access",
        "Efficiency",
        "Renewable Energy",
        "Public Lighting",
    ],
    "Urban Infrastructure": [
        "Roads",
        "Drainage",
        "Streetlights",
        "Public Spaces",
    ],
    "Accessibility": [
        "Mobility",
        "Assistive Infrastructure",
        "Inclusive Services",
    ],
    "Public Administration": [
        "Service Delivery",
        "Information Access",
        "Process Gaps",
    ],
    "Rural Livelihoods": [
        "Skills",
        "Employment",
        "Local Enterprises",
        "Market Access",
    ],
    "Other": [
        "Unclassified",
    ],
}


def get_domains() -> List[str]:
    """Return a list of all valid primary domains."""
    return list(TAXONOMY.keys())


def get_subcategories(domain: str) -> List[str]:
    """Return a list of subcategories for a given primary domain."""
    return TAXONOMY.get(domain, [])


def is_valid_domain(domain: str) -> bool:
    """Check if the given domain exists in the taxonomy."""
    return domain in TAXONOMY


def is_valid_subcategory(domain: str, subcategory: str) -> bool:
    """Check if the given subcategory is valid for the specified domain."""
    if not is_valid_domain(domain):
        return False
    return subcategory in TAXONOMY[domain]
