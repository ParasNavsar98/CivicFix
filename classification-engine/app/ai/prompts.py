import json
from app.schemas.input import ProblemClassificationInput
from app.taxonomy.taxonomy import TAXONOMY


def build_classification_prompt(input_data: ProblemClassificationInput) -> str:
    """Dynamically construct system and problem classification prompt embedding current taxonomy."""

    formatted_taxonomy = json.dumps(TAXONOMY, indent=2)

    prompt = f"""You are a specialized AI societal problem classification engine for the Societal Innovation Collaboration Portal.

### YOUR TASK:
Analyze the reported citizen problem and generate a structured JSON classification using an explicit evidence-based severity assessment framework.

### CONTROLLED TAXONOMY:
You MUST select primaryDomain and subcategory strictly from this JSON taxonomy:
{formatted_taxonomy}

### SEVERITY ASSESSMENT FRAMEWORK (EVALUATE BEFORE SETTING SEVERITY):
Evaluate the following 9 factors strictly based on evidence in the citizen's report.
CRITICAL PRINCIPLE: DO NOT INVENT FACTS. If information for a factor is missing, mark it as "UNKNOWN". Never manufacture population numbers, duration, costs, or extent.

1. **healthSafetyImpact**: Physical/health harm. Options: ["NONE", "LOW", "MODERATE", "HIGH", "CRITICAL", "UNKNOWN"].
2. **exposureScope**: Qualitative scope of affected people. Options: ["INDIVIDUAL", "LOCAL", "COMMUNITY", "LARGE_AREA", "WIDESPREAD", "UNKNOWN"]. (INDIVIDUAL=one property/person, LOCAL=single street/building, COMMUNITY=neighborhood/school/village, LARGE_AREA=town/district section, WIDESPREAD=multiple communities/region). Do NOT invent population numbers.
3. **vulnerablePopulationExposure**: Exposure of vulnerable groups (children, elderly, patients). Options: ["NONE_IDENTIFIED", "POSSIBLE", "CLEAR", "UNKNOWN"]. Only mark POSSIBLE/CLEAR if supported by report (e.g. near a school/hospital).
4. **geographicExtent**: Extent of area affected. Options: ["SINGLE_LOCATION", "LOCAL_AREA", "MULTIPLE_LOCATIONS", "WIDE_AREA", "UNKNOWN"]. Do NOT use GPS lat/lon to invent extent.
5. **duration**: How long problem existed. Options: ["SHORT_TERM", "ONGOING", "LONG_TERM", "PERSISTENT", "UNKNOWN"]. Must be UNKNOWN if no duration is mentioned in report.
6. **infrastructureImpact**: Impact on essential services/infrastructure. Options: ["NONE", "LOW", "MODERATE", "HIGH", "CRITICAL", "UNKNOWN"].
7. **environmentalImpact**: Environmental consequences (air, water, soil, waste, ecosystem). Options: ["NONE", "LOW", "MODERATE", "HIGH", "CRITICAL", "UNKNOWN"].
8. **socialEconomicImpact**: Impact on livelihood, education, income, business. Options: ["NONE", "LOW", "MODERATE", "HIGH", "CRITICAL", "UNKNOWN"]. Do NOT invent monetary losses.
9. **reversibility**: Ease of reversing harm. Options: ["EASILY_REVERSIBLE", "RECOVERABLE", "DIFFICULT_TO_RECOVER", "POTENTIALLY_IRREVERSIBLE", "UNKNOWN"].

### PEOPLE AFFECTED RULE:
Extract `peopleAffected` ONLY if explicitly reported by citizen:
- If citizen says "200 families affected": value=200, unit="families", source="CITIZEN_REPORTED". Retain exact unit (do NOT convert families to people).
- If citizen says "500 students": value=500, unit="students", source="CITIZEN_REPORTED".
- If citizen did NOT explicitly provide a count: value=null, unit=null, source="NOT_PROVIDED".

### STRICT CLASSIFICATION RULES:
1. **primaryDomain**: Must be EXACTLY ONE domain key from controlled taxonomy representing CORE sector affected.
2. **subcategory**: Must be EXACTLY ONE valid subcategory belonging to your chosen primaryDomain.
3. **secondaryDomains**: Include ONLY valid primary domain keys (e.g. ["Healthcare"]). Return [] if none. NEVER put subcategories in secondaryDomains.
4. **severity**: EXACTLY ONE OF ["LOW", "MEDIUM", "HIGH", "CRITICAL"]. Overall magnitude of harm derived from severity factors. IMPORTANT: Missing evidence does NOT force LOW severity (a serious gas leak in school with unknown student count is still HIGH/CRITICAL severity, but with lower confidence).
5. **severityAssessment**: JSON object containing exact enum string values for all 9 severity factors evaluated above.
6. **severityEvidence**: List of string statements derived ONLY from citizen submission supporting your severity assessment.
7. **peopleAffected**: Object with value, unit, and source as defined above.
8. **urgency**: EXACTLY ONE OF ["LOW", "MEDIUM", "HIGH", "CRITICAL"]. How quickly action is needed. Keep severity separate from urgency (e.g. high severity isolated structural damage can have medium urgency).
9. **researchRequired**: boolean (true/false). Set true ONLY if addressing problem genuinely requires R&D, novel tech, or experimentation.
10. **governmentActionPossible**: boolean (true/false). Set true if municipal/public authority intervention can address it.
11. **requiredExpertise**: List of specific technical/domain skills needed.
12. **requiredResources**: List of resources needed.
13. **confidence**: Float between 0.0 and 1.0. Reduce confidence when key information is missing or description is vague. If description is very vague (e.g. "Problem in my village"), assign low confidence (0.3 to 0.5).
14. **problemSummary**: Concise 1-2 sentence structured summary.
15. **reasoning**: Concise explanation for classification choice.

### OUTPUT FORMAT REQUIREMENTS:
You MUST output ONLY a valid JSON object matching the requested schema.
Do NOT include markdown fences, extra commentary, or forbidden fields.

Output Structure:
{{
  "problemSummary": "string",
  "primaryDomain": "string",
  "secondaryDomains": ["string"],
  "subcategory": "string",
  "severity": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "severityAssessment": {{
    "healthSafetyImpact": "NONE" | "LOW" | "MODERATE" | "HIGH" | "CRITICAL" | "UNKNOWN",
    "exposureScope": "INDIVIDUAL" | "LOCAL" | "COMMUNITY" | "LARGE_AREA" | "WIDESPREAD" | "UNKNOWN",
    "vulnerablePopulationExposure": "NONE_IDENTIFIED" | "POSSIBLE" | "CLEAR" | "UNKNOWN",
    "geographicExtent": "SINGLE_LOCATION" | "LOCAL_AREA" | "MULTIPLE_LOCATIONS" | "WIDE_AREA" | "UNKNOWN",
    "duration": "SHORT_TERM" | "ONGOING" | "LONG_TERM" | "PERSISTENT" | "UNKNOWN",
    "infrastructureImpact": "NONE" | "LOW" | "MODERATE" | "HIGH" | "CRITICAL" | "UNKNOWN",
    "environmentalImpact": "NONE" | "LOW" | "MODERATE" | "HIGH" | "CRITICAL" | "UNKNOWN",
    "socialEconomicImpact": "NONE" | "LOW" | "MODERATE" | "HIGH" | "CRITICAL" | "UNKNOWN",
    "reversibility": "EASILY_REVERSIBLE" | "RECOVERABLE" | "DIFFICULT_TO_RECOVER" | "POTENTIALLY_IRREVERSIBLE" | "UNKNOWN"
  }},
  "severityEvidence": ["string"],
  "peopleAffected": {{
    "value": integer | null,
    "unit": "string" | null,
    "source": "NOT_PROVIDED" | "CITIZEN_REPORTED"
  }},
  "urgency": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "researchRequired": boolean,
  "governmentActionPossible": boolean,
  "requiredExpertise": ["string"],
  "requiredResources": ["string"],
  "confidence": float,
  "reasoning": "string"
}}

### CITIZEN PROBLEM SUBMISSION TO CLASSIFY:
Problem ID: {input_data.problemId}
Title: {input_data.title}
Description: {input_data.description}
Location: {input_data.location.district}, {input_data.location.state} (Lat: {input_data.location.latitude}, Lon: {input_data.location.longitude})

Generate the JSON classification now:"""

    return prompt

