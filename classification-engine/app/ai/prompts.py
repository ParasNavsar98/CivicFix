import json
from app.schemas.input import ProblemClassificationInput
from app.taxonomy.taxonomy import TAXONOMY


def build_classification_prompt(input_data: ProblemClassificationInput) -> str:
    """Dynamically construct system and problem classification prompt embedding current taxonomy."""

    formatted_taxonomy = json.dumps(TAXONOMY, indent=2)

    prompt = f"""You are a specialized AI societal problem classification engine for the Societal Innovation Collaboration Portal.

### YOUR TASK:
Analyze the reported citizen problem and generate a structured JSON classification.

### CONTROLLED TAXONOMY:
You MUST select primaryDomain and subcategory strictly from this JSON taxonomy:
{formatted_taxonomy}

### STRICT CLASSIFICATION RULES:
1. **primaryDomain**: Must be EXACTLY ONE domain key from the controlled taxonomy above representing the CORE sector affected.
2. **subcategory**: Must be EXACTLY ONE valid subcategory belonging to your chosen primaryDomain. Do NOT use a subcategory from another domain or invent category names.
3. **secondaryDomains**: Actively evaluate if other primary domains are genuinely affected. Include ONLY valid primary domain keys (e.g., ["Healthcare", "Education"]). Return [] if no other domain is affected. NEVER place subcategories inside secondaryDomains (e.g., "Pollution" is a subcategory, NOT a domain).
4. **severity**: Must be EXACTLY ONE OF uppercase string values ["LOW", "MEDIUM", "HIGH", "CRITICAL"]. Represents the magnitude of harm/impact. Do not automatically set everything to HIGH.
5. **urgency**: Must be EXACTLY ONE OF uppercase string values ["LOW", "MEDIUM", "HIGH", "CRITICAL"]. Represents how quickly action is needed. Distinguish urgency from severity.
6. **researchRequired**: boolean (true/false). Set true ONLY if addressing the problem genuinely requires R&D, novel technical innovation, experimentation, or developing a new low-cost technology. Set false for ordinary infrastructure damage, missing standard equipment, routine garbage collection, or standard civil repairs.
7. **governmentActionPossible**: boolean (true/false). Set true if public-authority, municipal, or civic body intervention could reasonably address the reported problem.
8. **requiredExpertise**: List of specific technical/domain skills needed (e.g., ["Environmental Engineering", "Waste Management"]).
9. **requiredResources**: List of resources needed to solve or mitigate the problem (e.g., ["Waste collection vehicles", "Clean water treatment kit"]).
10. **confidence**: Float between 0.0 and 1.0. If the description is vague, ambiguous, or lacks specific context (e.g. "There is a problem in my village"), assign a LOW confidence score (0.3 to 0.5).
11. **problemSummary**: A concise 1-2 sentence structured summary of the problem.
12. **reasoning**: A concise justification explaining the classification choice.

### OUTPUT FORMAT REQUIREMENTS:
You MUST output ONLY a valid JSON object matching the requested schema.
Do NOT include markdown fences, extra commentary, explanations, or additional fields such as "additionalNotes", "explanation", or "comments".

Output Structure:
{{
  "problemSummary": "string",
  "primaryDomain": "string",
  "secondaryDomains": ["string"],
  "subcategory": "string",
  "severity": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
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
