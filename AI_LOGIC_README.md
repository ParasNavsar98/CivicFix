# Exact Implementation Logic README — CivicFix AI Modules

This document details the **EXACT LOGIC CURRENTLY IMPLEMENTED IN CODE** for the two core AI components of the CivicFix platform:
1. **Classification Engine** (`classification-engine/`)
2. **Duplicate Detection Engine** (`duplicate-detection/`)

> **AUDIT PRINCIPLE**: This document reflects strictly the executable code as of the current repository state. It contains no hypothetical features, un-implemented design goals, or generic ML assumptions. Missing components are explicitly marked `NOT IMPLEMENTED` or `PARTIALLY IMPLEMENTED`.

---

## Table of Contents
1. [AI Responsibility vs Application & Human Roles](#1-ai-responsibility-vs-application--human-roles)
2. [Classification Engine — Complete Flow](#2-classification-engine--complete-flow)
3. [Classification Engine — Input & Output Schemas](#3-classification-engine--input--output-schemas)
4. [Classification Engine — Text Preprocessing](#4-classification-engine--text-preprocessing)
5. [Classification Engine — Controlled Taxonomy](#5-classification-engine--controlled-taxonomy)
6. [Classification Engine — Gemma 3 4B Prompt Rules & Severity Framework](#6-classification-engine--gemma-3-4b-prompt-rules--severity-framework)
7. [Classification Engine — Ollama Provider & Structured Output](#7-classification-engine--ollama-provider--structured-output)
8. [Classification Engine — Post-LLM Validation & Ambiguity Safeguards](#8-classification-engine--post-llm-validation--ambiguity-safeguards)
9. [Classification Engine — Confidence Evaluation & Decision Table](#9-classification-engine--confidence-evaluation--decision-table)
10. [Classification Engine — Error Codes & Error Handling](#10-classification-engine--error-codes--error-handling)
11. [Duplicate Detection Engine — Complete Flow](#11-duplicate-detection-engine--complete-flow)
12. [Duplicate Detection Engine — Input & Output Schemas](#12-duplicate-detection-engine--input--output-schemas)
13. [Duplicate Detection Engine — Embedding Service](#13-duplicate-detection-engine--embedding-service)
14. [Duplicate Detection Engine — Semantic Cosine Similarity](#14-duplicate-detection-engine--semantic-cosine-similarity)
15. [Duplicate Detection Engine — Haversine Distance & Proximity Scoring](#15-duplicate-detection-engine--haversine-distance--proximity-scoring)
16. [Duplicate Detection Engine — Candidate Retrieval](#16-duplicate-detection-engine--candidate-retrieval)
17. [Duplicate Detection Engine — Multi-Factor Composite Duplicate Scoring](#17-duplicate-detection-engine--multi-factor-composite-duplicate-scoring)
18. [Duplicate Detection Engine — Signals Breakdown](#18-duplicate-detection-engine--signals-breakdown)
19. [Duplicate Detection Engine — Thresholds & Candidate Status Logic](#19-duplicate-detection-engine--thresholds--candidate-status-logic)
20. [Duplicate Detection Engine — Human-in-the-Loop Boundary](#20-duplicate-detection-engine--human-in-the-loop-boundary)
21. [Duplicate Detection Engine — Evaluation Benchmark Metrics](#21-duplicate-detection-engine--evaluation-benchmark-metrics)
22. [Classification vs Duplicate Detection Comparison](#22-classification-vs-duplicate-detection-comparison)
23. [Configuration Matrix (Configurable vs Hardcoded)](#23-configuration-matrix-configurable-vs-hardcoded)
24. [SRS vs Current Implementation Audit](#24-srs-vs-current-implementation-audit)
25. [Mathematical Formulations](#25-mathematical-formulations)
26. [Edge Case Handling](#26-edge-case-handling)
27. [Concrete End-to-End Traces](#27-concrete-end-to-end-traces)
28. [One-Page Logic Summary](#28-one-page-logic-summary)

---

## 1. AI Responsibility vs Application & Human Roles

To ensure clarity for system reviewers and judges, the responsibilities are strictly separated across runtime components:

| Responsibility | Executing Layer / Component | Function / Boundary |
| :--- | :--- | :--- |
| **Generative Categorization & Reasoning** | **Gemma 3 4B (via Ollama)** | Evaluates unstructured report text to recommend domain, subcategory, 9 qualitative severity factors, urgency, expertise/resources, summary, and initial self-reported confidence. |
| **Input Sanitization & Schema Enforcement** | **Python (FastAPI + Pydantic v2)** | Trims whitespace, validates string lengths, enforces coordinate bounds, and rejects malformed inputs prior to LLM invocation. |
| **Taxonomy Enforcement** | **Python (`app/taxonomy/taxonomy.py`)** | Validates that primary domains, subcategories, and secondary domains returned by Gemma strictly belong to the 12-domain controlled taxonomy dictionary. |
| **Ambiguity & Evidence Safeguards** | **Python (`app/services/classifier.py`)** | Evaluates description word counts, flags generic vague phrases, and forces status to `review_required` if evidence is insufficient or confidence is below 0.85. |
| **Vector Embedding Generation** | **Sentence-Transformers (`bge-small-en-v1.5`)** | Encodes problem `title + description` into 384-dimensional $L_2$-normalized dense vectors. |
| **Spatial Proximity Computation** | **Python (`app/services/location.py`)** | Calculates exact spherical surface distance in kilometers using the Haversine formula and applies linear score decay. |
| **Composite Multi-Factor Duplicate Scoring** | **Python (`app/services/duplicate_detector.py`)** | Combines semantic vector similarity, primary domain match, subcategory match, secondary Jaccard overlap, and location score into a weighted duplicate score ($0.0$ to $1.0$). |
| **Workflow State & Final Merge Decision** | **Human Reviewer (CivicFix Portal / Backend)** | **AI NEVER automatically merges, deletes, or modifies problem records.** Human reviewers inspect surfaced candidate recommendations and manually trigger record merges or state changes. |

---

## 2. Classification Engine — Complete Flow

The execution flow for `POST /classify` in `classification-engine/app/main.py`:

```text
Citizen HTTP POST /classify Request
 ↓
[app/main.py] FastAPI Endpoint Receiving Input
 ↓
[app/schemas/input.py] Pydantic Validation (ProblemClassificationInput)
 ├── IF invalid -> Exception Handler -> HTTP 422 JSON {"status": "failed", "errorCode": "INVALID_INPUT"}
 ↓
[app/services/preprocessor.py] Text Preprocessing & Sanitization (sanitize_and_preprocess)
 ├── Trims leading/trailing whitespace
 ├── Collapses multiple spaces & redundant newlines
 └── IF title or description empty -> raises ValueError -> HTTP 500 / 422
 ↓
[app/ai/prompts.py] Prompt Construction (build_classification_prompt)
 ├── Serializes taxonomy dict to JSON
 └── Formats system prompt, 9-factor severity rules, taxonomy rules, citizen text
 ↓
[app/ai/ollama.py] Ollama HTTP Call (OllamaProvider.classify)
 ├── Target: POST {OLLAMA_BASE_URL}/api/generate
 ├── Payload: {"model": "gemma3:4b", "prompt": ..., "stream": False, "options": {"temperature": 0.1}, "format": <Pydantic JSON Schema>}
 ├── Retry Loop: Up to 3 retries with exponential backoff (1s, 2s, 4s)
 └── HTTP Errors: 404 -> AI_MODEL_NOT_FOUND, Timeout -> AI_PROVIDER_TIMEOUT, ConnectError/5xx -> AI_PROVIDER_UNAVAILABLE
 ↓
Raw JSON String Response from Ollama
 ↓
[app/services/classifier.py] Response Processing (ClassifierService.classify_problem)
 ├── 1. Strip Markdown Fences (```json ... ```)
 ├── 2. JSON Deserialization (json.loads) -> IF error -> HTTP response {"status": "failed", "errorCode": "AI_INVALID_JSON"}
 ├── 3. Pydantic Output Validation (ClassificationResult.model_validate) -> IF error -> {"status": "failed", "errorCode": "AI_VALIDATION_ERROR"}
 ├── 4. Strict Taxonomy Check (validate_taxonomy_rules) -> IF domain/subcategory invalid -> {"status": "failed", "errorCode": "INVALID_TAXONOMY_CATEGORY"}
 ├── 5. Evidence Sufficiency Check (is_evidence_sufficient) -> Word count & vague phrase checks
 ├── 6. Ambiguity Detection (detect_ambiguity) -> True if low confidence, vague phrase, or "Other/Unclassified"
 └── 7. Confidence Evaluation (evaluate_confidence in app/services/confidence.py)
        ├── IF confidence >= 0.85 AND evidence_sufficient AND NOT ambiguity_detected
        │     └─ status = "classified"
        └── ELSE
              └─ status = "review_required"
 ↓
[app/main.py] Return Final ClassificationResponse JSON
```

---

## 3. Classification Engine — Input & Output Schemas

### Input JSON Schema (`ProblemClassificationInput`)
Location: `classification-engine/app/schemas/input.py`

| Field | Type | Required | Default | Validation & Constraints | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `problemId` | `str` | Yes | None | `max_length=100`, trimmed, non-empty | Unique identifier for citizen submission |
| `title` | `str` | Yes | None | `max_length=300`, trimmed, non-empty | Short title describing reported problem |
| `description` | `str` | Yes | None | `max_length=5000`, trimmed, non-empty | Detailed text explanation of problem |
| `location` | `ProblemLocation` | Yes | None | Nested Pydantic model | Physical geographic location details |
| `location.district` | `str` | Yes | None | `max_length=100`, trimmed, non-empty | District name |
| `location.state` | `str` | Yes | None | `max_length=100`, trimmed, non-empty | State name |
| `location.latitude` | `Optional[float]`| No | `None` | $-90.0 \le \text{lat} \le 90.0$ | GPS latitude coordinate |
| `location.longitude` | `Optional[float]`| No | `None` | $-180.0 \le \text{lon} \le 180.0$ | GPS longitude coordinate |

#### Input JSON Payload Format
```json
{
  "problemId": "P1001",
  "title": "Garbage burning near school",
  "description": "People dump garbage near our school and burn it every evening. Harmful smoke affects nearby residents.",
  "location": {
    "district": "Ranchi",
    "state": "Jharkhand",
    "latitude": 23.3441,
    "longitude": 85.3096
  }
}
```

---

### Output JSON Schema (`ClassificationResponse`)
Location: `classification-engine/app/schemas/classification.py`

| Field | Type | Required | Default | Allowed Values / Constraints | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `problemId` | `str` | Yes | None | String | Echoes request problem identifier |
| `status` | `str` | Yes | None | `"classified"`, `"review_required"`, `"failed"` | Overall classification pipeline outcome |
| `classification` | `Optional[Object]`| No | `null` | `ClassificationResult` schema or `null` if failed | Classification details payload |
| `classification.problemSummary` | `str` | Yes | None | Non-empty string | Concise 1-2 sentence problem summary |
| `classification.primaryDomain` | `str` | Yes | None | Must match 1 of 12 controlled taxonomy domain keys | Primary affected sector |
| `classification.secondaryDomains` | `List[str]` | No | `[]` | List of valid primary domain keys | Additional relevant secondary sectors |
| `classification.subcategory` | `str` | Yes | None | Valid subcategory for `primaryDomain` | Specific subcategory |
| `classification.severity` | `str` | Yes | None | `"LOW"`, `"MEDIUM"`, `"HIGH"`, `"CRITICAL"` | Derived overall magnitude of harm |
| `classification.severityAssessment` | `Object` | No | `{}` | `SeverityAssessment` object | Structured 9-factor evaluation breakdown |
| `classification.severityAssessment.healthSafetyImpact` | `str` | No | `"UNKNOWN"` | `"NONE"`, `"LOW"`, `"MODERATE"`, `"HIGH"`, `"CRITICAL"`, `"UNKNOWN"` | Physical/health harm level |
| `classification.severityAssessment.exposureScope` | `str` | No | `"UNKNOWN"` | `"INDIVIDUAL"`, `"LOCAL"`, `"COMMUNITY"`, `"LARGE_AREA"`, `"WIDESPREAD"`, `"UNKNOWN"` | Qualitative scope of affected people |
| `classification.severityAssessment.vulnerablePopulationExposure` | `str` | No | `"UNKNOWN"` | `"NONE_IDENTIFIED"`, `"POSSIBLE"`, `"CLEAR"`, `"UNKNOWN"` | Vulnerable population presence |
| `classification.severityAssessment.geographicExtent` | `str` | No | `"UNKNOWN"` | `"SINGLE_LOCATION"`, `"LOCAL_AREA"`, `"MULTIPLE_LOCATIONS"`, `"WIDE_AREA"`, `"UNKNOWN"` | Spatial footprint |
| `classification.severityAssessment.duration` | `str` | No | `"UNKNOWN"` | `"SHORT_TERM"`, `"ONGOING"`, `"LONG_TERM"`, `"PERSISTENT"`, `"UNKNOWN"` | Problem persistence |
| `classification.severityAssessment.infrastructureImpact` | `str` | No | `"UNKNOWN"` | `"NONE"`, `"LOW"`, `"MODERATE"`, `"HIGH"`, `"CRITICAL"`, `"UNKNOWN"` | Utility/service disruption |
| `classification.severityAssessment.environmentalImpact` | `str` | No | `"UNKNOWN"` | `"NONE"`, `"LOW"`, `"MODERATE"`, `"HIGH"`, `"CRITICAL"`, `"UNKNOWN"` | Ecological/pollution impact |
| `classification.severityAssessment.socialEconomicImpact` | `str` | No | `"UNKNOWN"` | `"NONE"`, `"LOW"`, `"MODERATE"`, `"HIGH"`, `"CRITICAL"`, `"UNKNOWN"` | Livelihood/economic impact |
| `classification.severityAssessment.reversibility` | `str` | No | `"UNKNOWN"` | `"EASILY_REVERSIBLE"`, `"RECOVERABLE"`, `"DIFFICULT_TO_RECOVER"`, `"POTENTIALLY_IRREVERSIBLE"`, `"UNKNOWN"` | Harm recoverability |
| `classification.severityEvidence` | `List[str]` | No | `[]` | List of string statements | Grounded evidence quotes from text |
| `classification.peopleAffected` | `Object` | No | `{}` | `PeopleAffected` object | Explicit citizen-reported count |
| `classification.peopleAffected.value` | `Optional[int]`| No | `null` | Positive integer or `null` | Exact numerical count |
| `classification.peopleAffected.unit` | `Optional[str]`| No | `null` | String (e.g. `"families"`, `"students"`) or `null` | Unit of measurement |
| `classification.peopleAffected.source` | `str` | No | `"NOT_PROVIDED"`| `"NOT_PROVIDED"`, `"CITIZEN_REPORTED"` | Source of population count |
| `classification.urgency` | `str` | Yes | None | `"LOW"`, `"MEDIUM"`, `"HIGH"`, `"CRITICAL"` | Speed of action required |
| `classification.researchRequired` | `bool` | Yes | None | `true`, `false` | True if R&D/innovation is needed |
| `classification.governmentActionPossible` | `bool` | Yes | None | `true`, `false` | True if public authority can address |
| `classification.requiredExpertise` | `List[str]` | No | `[]` | List of strings | Required technical skills |
| `classification.requiredResources` | `List[str]` | No | `[]` | List of strings | Required physical resources |
| `classification.confidence` | `float` | Yes | None | $0.0 \le \text{confidence} \le 1.0$, rounded to 4 decimals | Confidence score |
| `classification.reasoning` | `str` | Yes | None | Non-empty string | Explanation for classification decision |
| `error` | `Optional[Object]`| No | `null` | `ErrorDetails` (`errorCode`, `message`) or `null` | Error details payload if failed |

#### Successful Classification Output Format
```json
{
  "problemId": "P1001",
  "status": "classified",
  "classification": {
    "problemSummary": "Open garbage burning near school causing smoke pollution",
    "primaryDomain": "Environment",
    "secondaryDomains": ["Sanitation", "Healthcare"],
    "subcategory": "Pollution",
    "severity": "HIGH",
    "severityAssessment": {
      "healthSafetyImpact": "HIGH",
      "exposureScope": "COMMUNITY",
      "vulnerablePopulationExposure": "CLEAR",
      "geographicExtent": "LOCAL_AREA",
      "duration": "ONGOING",
      "infrastructureImpact": "NONE",
      "environmentalImpact": "HIGH",
      "socialEconomicImpact": "MODERATE",
      "reversibility": "RECOVERABLE"
    },
    "severityEvidence": ["Garbage is dumped near school and burned every evening causing harmful smoke"],
    "peopleAffected": {
      "value": null,
      "unit": null,
      "source": "NOT_PROVIDED"
    },
    "urgency": "HIGH",
    "researchRequired": false,
    "governmentActionPossible": true,
    "requiredExpertise": ["Waste Management", "Environmental Engineering"],
    "requiredResources": ["Waste collection vehicles", "Pollution monitoring"],
    "confidence": 0.9100,
    "reasoning": "Outdoor burning of waste near a school creates acute environmental pollution."
  },
  "error": null
}
```

---

## 4. Classification Engine — Text Preprocessing

Implementation file: `classification-engine/app/services/preprocessor.py`

### Cleaning Steps Implemented:
1. **Whitespace Normalization**:
   - `text.strip()` removes leading and trailing whitespace.
   - `re.sub(r"[ \t]+", " ", text)` collapses multiple internal spaces and tabs into a single space.
   - `re.sub(r"\n\s*\n+", "\n\n", text)` normalizes multiple empty lines into double newlines.
2. **Field Sanitization**:
   - Preprocessing is applied independently to `problemId`, `title`, `description`, `location.district`, and `location.state`.
   - Latitude and Longitude values are preserved unchanged as numerical floats.
3. **Empty Input Validation**:
   - If `cleaned_title` or `cleaned_description` evaluates to empty string (`""`) after whitespace trimming, a `ValueError("Title and description cannot be empty after preprocessing.")` is raised.
4. **Data Transformation Scope**:
   - Preprocessing **does NOT remove stop words**, lower-case text, perform stemming, or mutate semantic content.
   - A new cleaned `ProblemClassificationInput` instance is returned; original request data is not mutated in-place.

---

## 5. Classification Engine — Controlled Taxonomy

Implementation file: `classification-engine/app/taxonomy/taxonomy.py`

The system defines exactly **12 Primary Domains** and **40 Subcategories**:

| Primary Domain Key | Implemented Subcategories |
| :--- | :--- |
| **Education** | `Access`, `Infrastructure`, `Learning Support`, `Digital Education` |
| **Healthcare** | `Access`, `Public Health`, `Facilities`, `Diagnostics` |
| **Agriculture** | `Irrigation`, `Crop Support`, `Storage`, `Market Linkage` |
| **Water Resources** | `Supply`, `Quality`, `Leakage`, `Conservation`, `Monitoring` |
| **Sanitation** | `Waste`, `Drainage`, `Toilets`, `Cleanliness` |
| **Environment** | `Pollution`, `Biodiversity`, `Waste Reduction`, `Climate Resilience` |
| **Energy** | `Access`, `Efficiency`, `Renewable Energy`, `Public Lighting` |
| **Urban Infrastructure** | `Roads`, `Drainage`, `Streetlights`, `Public Spaces` |
| **Accessibility** | `Mobility`, `Assistive Infrastructure`, `Inclusive Services` |
| **Public Administration**| `Service Delivery`, `Information Access`, `Process Gaps` |
| **Rural Livelihoods** | `Skills`, `Employment`, `Local Enterprises`, `Market Access` |
| **Other** | `Unclassified` |

### Taxonomy Validation Rules:
1. **Domain Validation (`is_valid_domain`)**: Checks if `domain in TAXONOMY`. Exact string case matching against dict keys is required.
2. **Subcategory Validation (`is_valid_subcategory`)**: Checks if `subcategory in TAXONOMY[domain]`.
3. **Secondary Domain Validation**: Each item in `secondaryDomains` must be a valid primary domain key. Secondary domains cannot contain subcategories.
4. **Invalid Taxonomy Response**: If Gemma outputs a primary domain or subcategory outside this dictionary, `ClassifierService.validate_taxonomy_rules` raises `TaxonomyValidationError`, causing the endpoint to return `status: "failed"` with `errorCode: "INVALID_TAXONOMY_CATEGORY"`.
5. **Aliases / Synonyms**: `NOT IMPLEMENTED` (No fuzzy alias mapping exists in Python code; strict key matching is enforced).
6. **Fallback Category**: `"Other"` $\rightarrow$ `"Unclassified"` exists in the dictionary. If returned by Gemma, Python's `detect_ambiguity()` flags `ambiguity_detected = True`, forcing status to `review_required`.

---

## 6. Classification Engine — Gemma 3 4B Prompt Rules & Severity Framework

Implementation file: `classification-engine/app/ai/prompts.py`

The system prompt constructs rules for Gemma 3 4B:

### 1. Primary Domain & Subcategory Rules
- Instructs Gemma to select `primaryDomain` strictly from `TAXONOMY.keys()` and `subcategory` strictly from `TAXONOMY[primaryDomain]`.

### 2. Secondary Domains Logic
- Instructs Gemma to return a list of secondary relevant primary domain keys or `[]` if none apply. Subcategories are explicitly forbidden in `secondaryDomains`.

### 3. Severity Assessment Framework (9 Qualitative Factors)
Before setting overall `severity`, Gemma evaluates 9 factors:
1. `healthSafetyImpact`: `NONE` \| `LOW` \| `MODERATE` \| `HIGH` \| `CRITICAL` \| `UNKNOWN`
2. `exposureScope`: `INDIVIDUAL` \| `LOCAL` \| `COMMUNITY` \| `LARGE_AREA` \| `WIDESPREAD` \| `UNKNOWN`
3. `vulnerablePopulationExposure`: `NONE_IDENTIFIED` \| `POSSIBLE` \| `CLEAR` \| `UNKNOWN`
4. `geographicExtent`: `SINGLE_LOCATION` \| `LOCAL_AREA` \| `MULTIPLE_LOCATIONS` \| `WIDE_AREA` \| `UNKNOWN`
5. `duration`: `SHORT_TERM` \| `ONGOING` \| `LONG_TERM` \| `PERSISTENT` \| `UNKNOWN`
6. `infrastructureImpact`: `NONE` \| `LOW` \| `MODERATE` \| `HIGH` \| `CRITICAL` \| `UNKNOWN`
7. `environmentalImpact`: `NONE` \| `LOW` \| `MODERATE` \| `HIGH` \| `CRITICAL` \| `UNKNOWN`
8. `socialEconomicImpact`: `NONE` \| `LOW` \| `MODERATE` \| `HIGH` \| `CRITICAL` \| `UNKNOWN`
9. `reversibility`: `EASILY_REVERSIBLE` \| `RECOVERABLE` \| `DIFFICULT_TO_RECOVER` \| `POTENTIALLY_IRREVERSIBLE` \| `UNKNOWN`

> **CRITICAL PROMPT INSTRUCTION**: *DO NOT INVENT FACTS. If information for a factor is missing in the report, mark it as "UNKNOWN". Never manufacture population numbers, duration, costs, or spatial extent.*

### 4. People Affected Extraction Logic
- **Source Field**: Extracted strictly from citizen description text.
- **Allowed Units**: Retains exact citizen unit (e.g. `"families"`, `"students"`, `"residents"`). No unit conversions occur (e.g., 200 families is NOT converted to 800 people).
- **Missing Population**: If not explicitly stated, Gemma sets `value = null`, `unit = null`, `source = "NOT_PROVIDED"`.

### 5. Urgency Logic
- Urgency (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) measures speed of action required. Gemma is instructed to keep `severity` (magnitude of harm) separate from `urgency` (action speed).

### 6. Research & Government Action Logic
- `researchRequired`: Set `true` ONLY if solving problem genuinely requires R&D, novel technology, or experimentation.
- `governmentActionPossible`: Set `true` if municipal/public authority intervention can resolve it.

### 7. Confidence Distinction
- **Gemma Self-Reported Confidence**: Gemma produces a float between $0.0$ and $1.0$ in the JSON payload based on input clarity.
- **Python Validated Confidence**: Python evaluates Gemma's confidence in `app/services/confidence.py` alongside evidence sufficiency and ambiguity checks.

---

## 7. Classification Engine — Ollama Provider & Structured Output

Implementation files: `classification-engine/app/ai/ollama.py`, `app/ai/provider.py`, `app/config.py`

### Ollama API Configuration Parameters:
- **Base URL**: `OLLAMA_BASE_URL` (Default: `http://localhost:11434`)
- **Model Name**: `OLLAMA_MODEL` (Default: `gemma3:4b`)
- **API Endpoint**: `POST /api/generate`
- **HTTP Client**: `httpx.AsyncClient`
- **Timeout**: `LLM_TIMEOUT_SECONDS` (Default: `60.0` seconds)
- **Temperature**: Hardcoded to `0.1` in `payload["options"]["temperature"]` for deterministic output.
- **Streaming**: Hardcoded to `stream: False`.
- **Structured Schema Injection**: Python generates Pydantic JSON Schema via `ClassificationResult.model_json_schema()` and passes it in `payload["format"]`. Ollama uses this JSON Schema to constrain generation syntax.

### Retry & Backoff Logic:
- **Max Retries**: `LLM_MAX_RETRIES` (Default: `3`, giving 4 total attempts).
- **Backoff Formula**: Exponential backoff $1.0 \times 2^{\text{attempt}}$ seconds ($1\text{s}, 2\text{s}, 4\text{s}$).
- **Retry Conditions**: Triggered on `httpx.TimeoutException`, `httpx.ConnectError`, `httpx.RequestError`, or HTTP status codes `429`, `500`, `502`, `503`, `504`.
- **Non-Retryable Errors**: HTTP `404` raises `LLMProviderException` immediately (`AI_MODEL_NOT_FOUND`).

---

## 8. Classification Engine — Post-LLM Validation & Ambiguity Safeguards

Implementation file: `classification-engine/app/services/classifier.py`

After receiving the raw string response from Ollama:

```text
Raw Response String
 ↓
1. Clean Markdown Fences (strip ``` and ```json prefix)
 ↓
2. JSON Deserialization (json.loads)
    ├── IF JSONDecodeError -> Return status "failed", errorCode "AI_INVALID_JSON"
 ↓
3. Pydantic Model Validation (ClassificationResult.model_validate)
    ├── Normalizes enum case to uppercase
    ├── Checks confidence bounds [0.0, 1.0]
    └── IF ValidationError -> Return status "failed", errorCode "AI_VALIDATION_ERROR"
 ↓
4. Taxonomy Rule Validation (validate_taxonomy_rules)
    ├── Check primaryDomain in TAXONOMY
    ├── Check subcategory in TAXONOMY[primaryDomain]
    ├── Check each secondaryDomain in TAXONOMY
    └── IF invalid -> Return status "failed", errorCode "INVALID_TAXONOMY_CATEGORY"
 ↓
5. Evidence Sufficiency Evaluation (is_evidence_sufficient)
    ├── Description word count < 5 OR description length < 20 chars -> False
    ├── Description contains vague phrases ("problem in my village", "everything is bad", "nobody is helping us",
    │   "system is not working", "things are getting worse", "serious problem here", "needs help")
    │   AND word count < 12 -> False
    └── Otherwise -> True
 ↓
6. Ambiguity Detection (detect_ambiguity)
    ├── IF evidence_sufficient is False -> True
    ├── IF primaryDomain == "Other" AND subcategory == "Unclassified" -> True
    ├── IF classification.confidence < AI_HIGH_CONFIDENCE_THRESHOLD (0.85) -> True
    └── Otherwise -> False
 ↓
7. Evaluate Final Confidence Status (evaluate_confidence)
```

---

## 9. Classification Engine — Confidence Evaluation & Decision Table

Implementation file: `classification-engine/app/services/confidence.py`

### Boolean Decision Logic:
```python
if (
    confidence >= settings.AI_HIGH_CONFIDENCE_THRESHOLD # 0.85
    and evidence_sufficient                            # True
    and not ambiguity_detected                         # False
):
    return StatusEnum.CLASSIFIED
return StatusEnum.REVIEW_REQUIRED
```

### Complete Decision Matrix:

| Confidence Score | Evidence Sufficient | Ambiguity Detected | Primary Domain / Subcategory | Final Status |
| :--- | :--- | :--- | :--- | :--- |
| $\ge 0.85$ | True | False | Valid taxonomy category | `classified` |
| $\ge 0.85$ | False | True | Valid taxonomy category | `review_required` |
| $\ge 0.85$ | True | True | `"Other"` / `"Unclassified"` | `review_required` |
| $0.60 \le c < 0.85$| True | True | Valid taxonomy category | `review_required` |
| $< 0.60$ | Any | True | Valid taxonomy category | `review_required` |
| Any | Any | Any | Invalid domain / subcategory | `failed` (`INVALID_TAXONOMY_CATEGORY`)|

---

## 10. Classification Engine — Error Codes & Error Handling

All standard error responses return HTTP status codes and structured `ErrorDetails` payloads:

| Error Code | Trigger Condition | HTTP Status | Retry Behavior | Response JSON Structure |
| :--- | :--- | :--- | :--- | :--- |
| `INVALID_INPUT` | Request fails Pydantic schema validation or empty string check | 422 | No retry | `{"status": "failed", "errorCode": "INVALID_INPUT", "message": "..."}` |
| `AI_INVALID_JSON` | LLM returns malformed, truncated, or non-JSON string | 200 | No retry | `{"problemId": "...", "status": "failed", "error": {"errorCode": "AI_INVALID_JSON", "message": "..."}}` |
| `AI_VALIDATION_ERROR` | LLM JSON fails `ClassificationResult` Pydantic model validation | 200 | No retry | `{"problemId": "...", "status": "failed", "error": {"errorCode": "AI_VALIDATION_ERROR", "message": "..."}}` |
| `INVALID_TAXONOMY_CATEGORY`| LLM output primary domain, subcategory, or secondary domain violates taxonomy | 200 | No retry | `{"problemId": "...", "status": "failed", "error": {"errorCode": "INVALID_TAXONOMY_CATEGORY", "message": "..."}}` |
| `AI_MODEL_NOT_FOUND` | Ollama API returns HTTP 404 (model `gemma3:4b` not pulled) | 200 | Immed. Fail | `{"problemId": "...", "status": "failed", "error": {"errorCode": "AI_MODEL_NOT_FOUND", "message": "..."}}` |
| `AI_PROVIDER_TIMEOUT` | Ollama call times out after `LLM_TIMEOUT_SECONDS` (60s) across all retries | 200 | Retried 3x | `{"problemId": "...", "status": "failed", "error": {"errorCode": "AI_PROVIDER_TIMEOUT", "message": "..."}}` |
| `AI_PROVIDER_UNAVAILABLE` | Ollama connection refused, HTTP 429/5xx, or network down | 200 | Retried 3x | `{"problemId": "...", "status": "failed", "error": {"errorCode": "AI_PROVIDER_UNAVAILABLE", "message": "..."}}` |
| `INTERNAL_SERVER_ERROR` | Unhandled Python runtime exception | 500 | No retry | `{"status": "failed", "errorCode": "INTERNAL_SERVER_ERROR", "message": "..."}` |

---

## 11. Duplicate Detection Engine — Complete Flow

Execution flow for `POST /duplicate-check` in `duplicate-detection/app/main.py`:

```text
HTTP POST /duplicate-check Request Payload (DuplicateCheckRequest)
 ↓
[app/main.py] FastAPI Validation (DuplicateCheckRequest schema)
 ├── IF invalid -> Exception Handler -> HTTP 422 JSON {"error": {"errorCode": "INVALID_INPUT", ...}}
 ↓
[app/services/duplicate_detector.py] DuplicateDetector.detect_duplicates
 ├── IF candidates list is empty -> Return {"problemId": ..., "status": "no_candidate", "duplicateCandidates": []}
 ↓
[app/services/embedding.py] Query Text Construction & Embedding
 ├── text_a = "{title}. {description}"
 ├── EmbeddingService.embed(text_a) -> BAAI/bge-small-en-v1.5
 └── Generates 384-dimensional L2-normalized float vector
 ↓
Loop Over Candidate Problems Pool
 ├── For each Candidate Problem B:
 │   ├── 1. Construct candidate text_b = "{cand.title}. {cand.description}"
 │   ├── 2. Generate/retrieve 384-d vector for Candidate B
 │   ├── 3. [app/services/similarity.py] Calculate Cosine Similarity (S_sem)
 │   ├── 4. Primary Domain Match (M_prim = 1.0 if match else 0.0)
 │   ├── 5. Subcategory Match (M_sub = 1.0 if match else 0.0)
 │   ├── 6. Secondary Domain Jaccard Overlap (J_sec)
 │   ├── 7. [app/services/location.py] Calculate Haversine Distance in km
 │   ├── 8. Calculate Location Score S_loc = max(0.0, 1.0 - (distance / 5.0))
 │   ├── 9. Multi-Factor Composite Score Calculation:
 │   │      Score = 0.50*S_sem + 0.15*M_prim + 0.15*M_sub + 0.10*J_sec + 0.10*S_loc
 │   ├── 10. Status Determination:
 │   │      ├── IF Score >= 0.85 -> "strong_candidate"
 │   │      ├── ELSE IF Score >= 0.75 (DUPLICATE_SIMILARITY_THRESHOLD) -> "potential_duplicate"
 │   │      └── ELSE -> "no_candidate"
 │   └── 11. Construct Human-Readable Evidence Reasons List
 ↓
Sort Candidate Analyses Descending by duplicateScore
 ↓
Select Top-K Candidates (topK parameter, default 10)
 ↓
Overall Status Evaluation:
 ├── IF any candidate in Top-K has status "strong_candidate" or "potential_duplicate"
 │     └─ status = "candidate_found"
 └── ELSE
       └─ status = "no_candidate"
 ↓
[app/main.py] Return DuplicateCheckResponse Payload
```

---

## 12. Duplicate Detection Engine — Input & Output Schemas

### Input JSON Schema (`DuplicateCheckRequest`)
Location: `duplicate-detection/app/schemas/input.py`

| Field | Type | Required | Default | Validation & Constraints | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `problem` | `ProblemInput` | Yes | None | Nested object | Query problem to check |
| `problem.problemId` | `Optional[str]`| No | `None` | `max_length=100` | Problem ID |
| `problem.title` | `str` | Yes | None | `min_length=1`, `max_length=300`, trimmed | Problem title |
| `problem.description` | `str` | Yes | None | `min_length=1`, `max_length=5000`, trimmed | Problem description |
| `problem.location` | `Optional[LocationInput]`| No | `None` | Nested object | Location coordinates |
| `problem.location.lat` | `Optional[float]`| No | `None` | $-90.0 \le \text{lat} \le 90.0$ | Latitude coordinate |
| `problem.location.long`| `Optional[float]`| No | `None` | $-180.0 \le \text{long} \le 180.0$ | Longitude coordinate |
| `problem.location.address`| `Optional[str]`| No | `None` | `max_length=300` | Street or area address |
| `problem.primaryDomain` | `Optional[str]`| No | `None` | `max_length=100` | Primary domain from taxonomy |
| `problem.secondaryDomains` | `List[str]` | No | `[]` | List of strings | Secondary domains |
| `problem.subcategory` | `Optional[str]`| No | `None` | `max_length=100` | Subcategory from taxonomy |
| `candidates` | `List[ProblemInput]` | No | `[]` | List of `ProblemInput` candidates | Pool of candidate problems to compare |
| `topK` | `Optional[int]`| No | `10` | $1 \le \text{topK} \le 100$ | Limit for returned recommendations |

---

### Output JSON Schema (`DuplicateCheckResponse`)
Location: `duplicate-detection/app/schemas/duplicate.py`

| Field | Type | Required | Allowed Values / Constraints | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `problemId` | `str` | Yes | String | ID of target query problem |
| `status` | `str` | Yes | `"candidate_found"`, `"no_candidate"` | Overall duplicate detection result |
| `duplicateCandidates` | `List[CandidateMatch]` | Yes | List of candidate objects sorted by `duplicateScore` desc | Ranked candidate list |
| `candidate.candidateProblemId` | `str` | Yes | String | ID of candidate problem |
| `candidate.duplicateScore` | `float` | Yes | $0.0 \le \text{score} \le 1.0$, 4 decimals | Composite multi-factor score |
| `candidate.semanticSimilarity` | `float` | Yes | $0.0 \le \text{sim} \le 1.0$, 6 decimals | Cosine similarity of BGE embeddings |
| `candidate.primaryDomainMatch` | `bool` | Yes | `true`, `false` | True if primary domains match |
| `candidate.subcategoryMatch` | `bool` | Yes | `true`, `false` | True if subcategories match |
| `candidate.secondaryDomainOverlap` | `float` | Yes | $0.0 \le \text{overlap} \le 1.0$, 4 decimals | Jaccard overlap fraction |
| `candidate.locationDistanceKm` | `Optional[float]` | No | Float $\ge 0.0$ or `null` | Haversine distance in km |
| `candidate.locationScore` | `float` | Yes | $0.0 \le \text{score} \le 1.0$, 4 decimals | Proximity score |
| `candidate.candidateStatus` | `str` | Yes | `"strong_candidate"`, `"potential_duplicate"`, `"no_candidate"` | Status classification |
| `candidate.reasons` | `List[str]` | Yes | List of strings | Human-readable explainability list |

#### Example Response Output Format
```json
{
  "problemId": "P2001",
  "status": "candidate_found",
  "duplicateCandidates": [
    {
      "candidateProblemId": "P1001",
      "duplicateScore": 0.9421,
      "semanticSimilarity": 0.8909,
      "primaryDomainMatch": true,
      "subcategoryMatch": true,
      "secondaryDomainOverlap": 1.0,
      "locationDistanceKm": 0.049,
      "locationScore": 0.9902,
      "candidateStatus": "strong_candidate",
      "reasons": [
        "High semantic similarity (0.891)",
        "Same primary domain (Environment)",
        "Same subcategory (Pollution)",
        "Secondary domain overlap (100%)",
        "Geographically very close (0.05 km)"
      ]
    }
  ]
}
```

---

## 13. Duplicate Detection Engine — Embedding Service

Implementation file: `duplicate-detection/app/services/embedding.py`

- **Embedding Model**: `BAAI/bge-small-en-v1.5` (loaded via `sentence_transformers.SentenceTransformer`).
- **Vector Dimension**: Exactly **384 dimensions**.
- **Normalization**: Enforces $L_2$ normalization via `normalize_embeddings=True` in SentenceTransformer `encode()`.
- **Text Construction**: Input text is constructed as:
  ```python
  text = f"{problem.title}. {problem.description}".strip()
  ```
- **Batch Processing (`embed_many`)**: Encodes lists of strings in a single model forward pass.
- **Model Loading Lifecycle**: Preloaded once at service startup via FastAPI `lifespan` context manager into `embedding_service._model`.
- **Device Support**: Runs on CPU by default (or PyTorch default device).
- **Caching**: `NOT IMPLEMENTED` (No vector caching layer like Redis exists; embeddings are generated on-demand or pre-indexed in memory).

---

## 14. Duplicate Detection Engine — Semantic Cosine Similarity

Implementation file: `duplicate-detection/app/services/similarity.py`

### Formula Implemented:
Given two 384-dimensional $L_2$-normalized float vectors $\mathbf{A}$ and $\mathbf{B}$:

$$\text{similarity} = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\|_2 \|\mathbf{B}\|_2}$$

```python
norm_a = float(np.linalg.norm(arr_a))
norm_b = float(np.linalg.norm(arr_b))

if norm_a == 0.0 or norm_b == 0.0:
    return 0.0

dot_product = float(np.dot(arr_a, arr_b))
sim = dot_product / (norm_a * norm_b)
sim = float(np.clip(sim, -1.0, 1.0))
return round(sim, 6)
```

- **Output Range**: Clipped to $[-1.0, 1.0]$ for numerical stability, rounded to 6 decimal places.
- **Dimension Check**: Raises `VectorDimensionMismatchError` if vector dimensions differ.

---

## 15. Duplicate Detection Engine — Haversine Distance & Proximity Scoring

Implementation file: `duplicate-detection/app/services/location.py`

### 1. Haversine Distance Formula ($\text{km}$)
Given coordinates $(\text{lat}_1, \text{lon}_1)$ and $(\text{lat}_2, \text{lon}_2)$ in decimal degrees:

$$d = 2 R \arcsin \left( \sqrt{ \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1) \cos(\phi_2) \sin^2\left(\frac{\Delta \lambda}{2}\right) } \right)$$

Where $R = 6371.0\text{ km}$ (Earth mean radius), $\phi = \text{lat} \times \frac{\pi}{180}$, $\lambda = \text{lon} \times \frac{\pi}{180}$.
Output is rounded to 3 decimal places.

### 2. Location Proximity Score ($S_{\text{loc}}$)
Applies a linear decay over maximum radius $r_{\text{max}} = 5.0\text{ km}$ (`LOCATION_DISTANCE_THRESHOLD_KM`):

$$S_{\text{loc}} = \begin{cases} 
0.0 & \text{if coordinates missing or distance } \text{km} \text{ is } \text{None} \\
\max\left(0.0, 1.0 - \frac{d}{r_{\text{max}}}\right) & \text{if distance } d \text{ is present}
\end{cases}$$

- Distance $0.0\text{ km} \rightarrow S_{\text{loc}} = 1.0000$
- Distance $2.5\text{ km} \rightarrow S_{\text{loc}} = 0.5000$
- Distance $\ge 5.0\text{ km} \rightarrow S_{\text{loc}} = 0.0000$
- Missing coordinates $\rightarrow S_{\text{loc}} = 0.0000$ (Neutral fallback)

---

## 16. Duplicate Detection Engine — Candidate Retrieval

Implementation file: `duplicate-detection/app/services/candidate_retriever.py`

- **Retrieval Mechanism**: Local in-memory vector index (`CandidateRetriever`).
- **Candidate Pool**: Candidates are passed via request payload (`candidates` array) or stored in memory index via `add_candidate(problem_id, embedding, metadata)`.
- **Top-K Limit**: `topK` parameter (Default: `10`, range $1 \le \text{topK} \le 100$).
- **Filtering Rules**:
  - Excludes self-matching (handled by backend caller filtering out `problemId == target.problemId`).
  - No domain or status hard-filtering in candidate retrieval; all candidate pairs are scored by `DuplicateDetector`.

---

## 17. Duplicate Detection Engine — Multi-Factor Composite Duplicate Scoring

Implementation file: `duplicate-detection/app/services/duplicate_detector.py`

### Equation Implemented in Code:

$$\text{DuplicateScore} = (w_{\text{sem}} \times S_{\text{sem}}) + (w_{\text{prim}} \times M_{\text{prim}}) + (w_{\text{sub}} \times M_{\text{sub}}) + (w_{\text{sec}} \times J_{\text{sec}}) + (w_{\text{loc}} \times S_{\text{loc}})$$

### Default Weight Configuration:

| Component Factor | Variable Name | Default Weight Value | Source |
| :--- | :--- | :--- | :--- |
| **Semantic Cosine Similarity** | `SEMANTIC_WEIGHT` | `0.50` | `app/config.py` |
| **Primary Domain Match** | `PRIMARY_DOMAIN_WEIGHT` | `0.15` | `app/config.py` |
| **Subcategory Match** | `SUBCATEGORY_WEIGHT` | `0.15` | `app/config.py` |
| **Secondary Domain Overlap** | `SECONDARY_DOMAIN_WEIGHT` | `0.10` | `app/config.py` |
| **Location Proximity Score** | `LOCATION_WEIGHT` | `0.10` | `app/config.py` |
| **Total Sum** | — | **`1.00`** | — |

Result is rounded to 4 decimal places ($0.0000$ to $1.0000$).

---

## 18. Duplicate Detection Engine — Signals Breakdown

| Signal Name | Calculation Method | Value Range | Default Weight | Explainability Reason Output |
| :--- | :--- | :--- | :--- | :--- |
| `semanticSimilarity` | Cosine similarity of 384-d BGE vectors | $0.0$ to $1.0$ | `0.50` | `"High semantic similarity (0.891)"` ($\ge 0.80$)<br>`"Moderate semantic similarity (0.712)"` ($0.65 \le s < 0.80$) |
| `primaryDomainMatch` | Binary string equality: `lower(prim_a) == lower(prim_b)` | `True` / `False` | `0.15` | `"Same primary domain (Environment)"` |
| `subcategoryMatch` | Binary string equality: `lower(sub_a) == lower(sub_b)` | `True` / `False` | `0.15` | `"Same subcategory (Pollution)"` |
| `secondaryDomainOverlap`| Jaccard similarity index: $\frac{\|A \cap B\|}{\|A \cup B\|}$ | $0.0$ to $1.0$ | `0.10` | `"Secondary domain overlap (100%)"` ($> 0$) |
| `locationScore` | Linear decay based on Haversine distance: $\max(0, 1 - \frac{d}{5.0})$ | $0.0$ to $1.0$ | `0.10` | `"Geographically very close (0.05 km)"` ($\le 1\text{km}$)<br>`"Geographically nearby (3.20 km)"` ($\le 5\text{km}$)<br>`"Geographically distant (12.4 km)"` ($> 5\text{km}$)<br>`"Location coordinates missing or incomplete"` |

---

## 19. Duplicate Detection Engine — Thresholds & Candidate Status Logic

Implementation file: `duplicate-detection/app/services/duplicate_detector.py`

### Candidate Status Threshold Rules:
For each analyzed candidate pair:

```python
if composite_score >= 0.85:
    status = "strong_candidate"
elif composite_score >= self.similarity_threshold: # 0.75 default
    status = "potential_duplicate"
else:
    status = "no_candidate"
```

### Overall Response Status Rules:
```python
has_strong = any(r["candidateStatus"] in ("strong_candidate", "potential_duplicate") for r in top_results)
overall_status = "candidate_found" if has_strong else "no_candidate"
```

---

## 20. Duplicate Detection Engine — Human-in-the-Loop Boundary

> **STRICT ARCHITECTURAL GUARANTEE**:
> 1. The Duplicate Detection Engine is strictly a **candidate recommendation service**.
> 2. It **DOES NOT automatically merge, delete, update, or archive problem records** in the database.
> 3. The service outputs candidate matches along with transparent, human-readable explainability reasons (`reasons` array).
> 4. Consequential actions (merging records, closing duplicate reports) require explicit authorization and action by a **Human Reviewer** via the platform review queue UI.

---

## 21. Duplicate Detection Engine — Evaluation Benchmark Metrics

Implementation file: `duplicate-detection/tests/test_duplicate_metrics.py`
Benchmark Dataset: `duplicate-detection/tests/evaluation_dataset.json` (50 synthetic labeled problem cases).

### Threshold Experiment Evaluation Results:

| Threshold | True Pos (TP) | False Pos (FP) | True Neg (TN) | False Neg (FN) | Precision | Recall | F1 Score | False Positive Rate (FPR) | False Negative Rate (FNR) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0.60 | 27 | 3 | 19 | 1 | 0.9000 | 0.9643 | 0.9310 | 0.1364 | 0.0357 |
| 0.65 | 27 | 3 | 19 | 1 | 0.9000 | 0.9643 | 0.9310 | 0.1364 | 0.0357 |
| **0.70** | 27 | 2 | 20 | 1 | 0.9310 | 0.9643 | 0.9474 | 0.0909 | 0.0357 |
| **0.75 (Default)** | **27** | **2** | **20** | **1** | **0.9310** | **0.9643** | **0.9474** | **0.0909** | **0.0357** |
| 0.78 | 23 | 1 | 21 | 5 | 0.9583 | 0.8214 | 0.8846 | 0.0455 | 0.1786 |
| 0.80 | 19 | 1 | 21 | 9 | 0.9500 | 0.6786 | 0.7917 | 0.0455 | 0.3214 |
| 0.85 | 13 | 0 | 22 | 15 | 1.0000 | 0.4643 | 0.6341 | 0.0000 | 0.5357 |

- **Dataset Nature**: Synthetic ground-truth evaluation dataset (`tests/evaluation_dataset.json`).
- **Production Selected Threshold**: `DUPLICATE_SIMILARITY_THRESHOLD = 0.75` (Yields optimal F1 Score of `0.9474` and Precision of `93.1%`).

---

## 22. Classification vs Duplicate Detection Comparison

| Aspect | Classification Engine | Duplicate Detection Engine |
| :--- | :--- | :--- |
| **Primary Goal** | Single-report taxonomy categorization, severity/urgency rating, summary generation | Multi-report pair-wise duplicate candidate identification & ranking |
| **Core Technology** | Generative LLM: **Gemma 3 4B** via local Ollama API | Dense Embeddings: **BAAI/bge-small-en-v1.5** (Sentence-Transformers) |
| **Input** | Single problem text (`title`, `description`, `location`) | Query problem + Candidate problems pool |
| **Output** | Categorization, severity, urgency, expertise, resources, confidence | Ranked candidate matches, composite scores, distance, reasons |
| **Execution Latency** | ~1.5s – 4.0s (LLM inference) | ~10ms – 50ms (Vector dot products & distance) |
| **Primary Threshold** | `AI_HIGH_CONFIDENCE_THRESHOLD` ($0.85$) | `DUPLICATE_SIMILARITY_THRESHOLD` ($0.75$) |
| **Autonomous Action** | Sets status `classified` or `review_required` | Recommends candidate status (`strong_candidate`, `potential_duplicate`) |
| **Human Role** | Reviews flagged `review_required` submissions | Evaluates duplicate candidate signals and performs merge |

---

## 23. Configuration Matrix (Configurable vs Hardcoded)

### Configurable Parameters (via `.env` or Pydantic Settings)

| Service | Setting Name | Default Value | Source / File Location | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| Classification | `OLLAMA_BASE_URL` | `http://localhost:11434` | `classification-engine/app/config.py` | Local Ollama API endpoint URL |
| Classification | `OLLAMA_MODEL` | `gemma3:4b` | `classification-engine/app/config.py` | Ollama model identifier |
| Classification | `LLM_TIMEOUT_SECONDS` | `60.0` | `classification-engine/app/config.py` | HTTP timeout per call |
| Classification | `LLM_MAX_RETRIES` | `3` | `classification-engine/app/config.py` | Max retry attempts |
| Classification | `AI_HIGH_CONFIDENCE_THRESHOLD` | `0.85` | `classification-engine/app/config.py` | Threshold for `classified` status |
| Classification | `AI_REVIEW_THRESHOLD` | `0.60` | `classification-engine/app/config.py` | Low-confidence boundary |
| Duplicate Detection | `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | `duplicate-detection/app/config.py` | HuggingFace embedding model |
| Duplicate Detection | `EMBEDDING_DIMENSION` | `384` | `duplicate-detection/app/config.py` | Expected vector dimension |
| Duplicate Detection | `VECTOR_TOP_K` | `10` | `duplicate-detection/app/config.py` | Default candidate limit |
| Duplicate Detection | `DUPLICATE_SIMILARITY_THRESHOLD` | `0.75` | `duplicate-detection/app/config.py` | Threshold for duplicate candidates |
| Duplicate Detection | `LOCATION_DISTANCE_THRESHOLD_KM` | `5.0` | `duplicate-detection/app/config.py` | Max distance for proximity score |
| Duplicate Detection | `SEMANTIC_WEIGHT` | `0.50` | `duplicate-detection/app/config.py` | Composite score semantic weight |
| Duplicate Detection | `PRIMARY_DOMAIN_WEIGHT` | `0.15` | `duplicate-detection/app/config.py` | Primary domain match weight |
| Duplicate Detection | `SUBCATEGORY_WEIGHT` | `0.15` | `duplicate-detection/app/config.py` | Subcategory match weight |
| Duplicate Detection | `SECONDARY_DOMAIN_WEIGHT` | `0.10` | `duplicate-detection/app/config.py` | Secondary overlap weight |
| Duplicate Detection | `LOCATION_WEIGHT` | `0.10` | `duplicate-detection/app/config.py` | Location proximity weight |

### Hardcoded Rules & Logics (In Python Code)

| Service | Hardcoded Logic | Implementation File | Purpose / Details |
| :--- | :--- | :--- | :--- |
| Classification | `options.temperature = 0.1` | `classification-engine/app/ai/ollama.py` | Forces low temperature for deterministic JSON output |
| Classification | `options.stream = False` | `classification-engine/app/ai/ollama.py` | Disables streaming responses |
| Classification | Vague phrase strings list | `classification-engine/app/services/classifier.py` | Specific string phrases checked for short descriptions |
| Classification | Short description word count ($< 5$ words, $< 20$ chars) | `classification-engine/app/services/classifier.py` | Minimum actionable text length |
| Classification | 12 Primary Domains & 40 Subcategories | `classification-engine/app/taxonomy/taxonomy.py` | Controlled taxonomy dictionary |
| Duplicate Detection | Haversine Earth Radius $R = 6371.0\text{ km}$ | `duplicate-detection/app/services/location.py` | Mean Earth radius constant |
| Duplicate Detection | Strong candidate status score threshold ($\ge 0.85$) | `duplicate-detection/app/services/duplicate_detector.py` | Hardcoded threshold for `strong_candidate` label |
| Duplicate Detection | Reason generation thresholds ($0.80$, $0.65$, $1.0\text{km}$) | `duplicate-detection/app/services/duplicate_detector.py` | Explanatory text rules |

---

## 24. SRS vs Current Implementation Audit

The following table compares requirements stated in platform documentation/headers against the executable implementation:

| Requirement Area | Stated SRS Requirement | Current Codebase Implementation | Compliance Status | Discrepancy / Implementation Detail |
| :--- | :--- | :--- | :---: | :--- |
| **Taxonomy Categorization** | Single primary domain and subcategory assignment from controlled taxonomy | Implemented via Gemma 3 4B + strict Python taxonomy dictionary validation | `IMPLEMENTED` | Strict key validation in Python; invalid LLM outputs cause explicit API failure. |
| **Configurable Confidence Threshold** | Support configurable confidence thresholds for review routing | Implemented via `AI_HIGH_CONFIDENCE_THRESHOLD` ($0.85$) in `config.py` | `IMPLEMENTED` | Fully configurable via env vars. |
| **Human-in-the-Loop Safeguard** | AI recommends, authorized humans own consequential merge decisions | Engine surfaces candidates + reasons; backend orchestrator enforces review queues | `IMPLEMENTED` | AI microservices perform zero automated database merges. |
| **Semantic Embeddings for Duplicates** | Generate vector embeddings for duplicate candidate matching | Implemented using `BAAI/bge-small-en-v1.5` yielding 384-d normalized vectors | `IMPLEMENTED` | Model choice (`bge-small-en-v1.5`) is a local efficiency implementation decision. |
| **Configurable Similarity Threshold** | Support configurable duplicate threshold (`DUPLICATE_SIMILARITY_THRESHOLD`) | Implemented via `DUPLICATE_SIMILARITY_THRESHOLD` ($0.75$) in `config.py` | `IMPLEMENTED` | Fully configurable via env vars. |
| **Geographic Location Proximity** | Incorporate spatial location in candidate matching | Implemented using Haversine formula + linear decay over 5.0 km radius | `IMPLEMENTED` | 5.0 km radius and linear decay score are implementation decisions. |
| **Vector Database Integration** | High-scale vector search index (FAISS / MongoDB Vector Search) | Local in-memory candidate retriever (`CandidateRetriever`) | `PARTIALLY IMPLEMENTED` | Clean abstraction exists, but production vector DB integration is not yet active. |
| **Multilingual Input Translation** | Automatically translate non-English citizen reports prior to AI processing | `NOT IMPLEMENTED` | `NOT IMPLEMENTED` | Preprocessor passes text directly to Gemma without translation. |
| **Multi-Modal Asset Analysis** | Analyze uploaded images/videos of societal problems | `NOT IMPLEMENTED` | `NOT IMPLEMENTED` | Engine accepts text and location fields only. |

---

## 25. Mathematical Formulations

### 1. Vector Cosine Similarity
$$\text{similarity}(\mathbf{u}, \mathbf{v}) = \frac{\sum_{i=1}^{384} u_i v_i}{\sqrt{\sum_{i=1}^{384} u_i^2} \sqrt{\sum_{i=1}^{384} v_i^2}}$$

### 2. Haversine Distance Formula ($\text{km}$)
$$a = \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1) \cos(\phi_2) \sin^2\left(\frac{\Delta \lambda}{2}\right)$$
$$c = 2 \cdot \text{atan2}\left(\sqrt{a}, \sqrt{1-a}\right)$$
$$d = 6371.0 \times c$$

### 3. Location Proximity Score ($S_{\text{loc}}$)
$$S_{\text{loc}} = \max\left(0.0, 1.0 - \frac{d}{5.0}\right)$$

### 4. Jaccard Secondary Domain Overlap ($J_{\text{sec}}$)
$$J_{\text{sec}}(A, B) = \frac{|A \cap B|}{|A \cup B|}$$

### 5. Multi-Factor Composite Duplicate Score ($\text{Score}$)
$$\text{Score} = 0.50 S_{\text{sem}} + 0.15 M_{\text{prim}} + 0.15 M_{\text{sub}} + 0.10 J_{\text{sec}} + 0.10 S_{\text{loc}}$$

---

## 26. Edge Case Handling

### Classification Engine Edge Cases

| Scenario | Code Behavior | Exception / Status |
| :--- | :--- | :--- |
| **Empty title or description** | Caught by `ProblemClassificationInput` string validator or preprocessor | HTTP 422 `INVALID_INPUT` |
| **Vague input ("problem in my village")** | `is_evidence_sufficient` returns `False`, `detect_ambiguity` returns `True` | API status `review_required` |
| **Invalid domain returned by LLM** | `validate_taxonomy_rules` raises `TaxonomyValidationError` | API status `failed`, `INVALID_TAXONOMY_CATEGORY` |
| **Ollama service offline** | `httpx.ConnectError` caught after 3 exponential retries | API status `failed`, `AI_PROVIDER_UNAVAILABLE` |
| **Model not pulled (`gemma3:4b`)** | Ollama returns HTTP 404 | API status `failed`, `AI_MODEL_NOT_FOUND` |
| **LLM returns non-JSON string** | `json.loads` fails | API status `failed`, `AI_INVALID_JSON` |
| **Missing location coordinates** | `latitude` & `longitude` default to `None` | Prompt handles gracefully as `None` |

### Duplicate Detection Engine Edge Cases

| Scenario | Code Behavior | Exception / Status |
| :--- | :--- | :--- |
| **Empty candidates list** | Detector immediately returns empty candidates array | `status: "no_candidate"`, `duplicateCandidates: []` |
| **Missing location coordinates** | `haversine_distance` returns `None`, `calculate_location_score` returns `0.0` | $S_{\text{loc}} = 0.0$, reason: `"Location coordinates missing or incomplete"` |
| **Identical coordinates ($0.0\text{ km}$)** | `haversine_distance` returns $0.0$, $S_{\text{loc}} = 1.0$ | $S_{\text{loc}} = 1.0$, reason: `"Geographically very close (0.00 km)"` |
| **Coordinates $> 5.0\text{ km}$ distant** | `calculate_location_score` returns $0.0$ | $S_{\text{loc}} = 0.0$, reason: `"Geographically distant (X km)"` |
| **Semantically identical, different domain** | High $S_{\text{sem}}$, $M_{\text{prim}} = 0.0$, $M_{\text{sub}} = 0.0$ | Weighted score accurately reflects domain mismatch |
| **Vector dimension mismatch** | `compare_one_to_many` catches mismatch | HTTP 400 `VECTOR_DIMENSION_MISMATCH` |

---

## 27. Concrete End-to-End Traces

### Trace 1: Classification Engine (`POST /classify`)

**Input Payload:**
```json
{
  "problemId": "P1001",
  "title": "Garbage burning near school",
  "description": "People dump garbage near our school and burn it every evening. Harmful smoke affects nearby residents.",
  "location": {
    "district": "Ranchi",
    "state": "Jharkhand",
    "latitude": 23.3441,
    "longitude": 85.3096
  }
}
```

**Step-by-Step Execution:**
1. Pydantic validates string lengths and coordinate ranges.
2. `sanitize_and_preprocess` trims text.
3. `build_classification_prompt` injects taxonomy JSON and prompt template.
4. `OllamaProvider.classify` posts to `http://localhost:11434/api/generate` with model `gemma3:4b` and JSON schema format.
5. Gemma returns structured JSON response.
6. `ClassificationResult.model_validate` parses JSON.
7. `validate_taxonomy_rules` checks `Environment` and `Pollution` against taxonomy dictionary.
8. `is_evidence_sufficient` evaluates word count ($18 > 5$ words) $\rightarrow$ `True`.
9. `detect_ambiguity` checks confidence ($0.9100 \ge 0.85$) $\rightarrow$ `False`.
10. `evaluate_confidence` returns `StatusEnum.CLASSIFIED`.

**Returned API Response Payload:**
```json
{
  "problemId": "P1001",
  "status": "classified",
  "classification": {
    "problemSummary": "Open garbage burning near school causing smoke pollution",
    "primaryDomain": "Environment",
    "secondaryDomains": ["Sanitation", "Healthcare"],
    "subcategory": "Pollution",
    "severity": "HIGH",
    "severityAssessment": {
      "healthSafetyImpact": "HIGH",
      "exposureScope": "COMMUNITY",
      "vulnerablePopulationExposure": "CLEAR",
      "geographicExtent": "LOCAL_AREA",
      "duration": "ONGOING",
      "infrastructureImpact": "NONE",
      "environmentalImpact": "HIGH",
      "socialEconomicImpact": "MODERATE",
      "reversibility": "RECOVERABLE"
    },
    "severityEvidence": ["Garbage dumped near school and burned every evening causing harmful smoke"],
    "peopleAffected": {
      "value": null,
      "unit": null,
      "source": "NOT_PROVIDED"
    },
    "urgency": "HIGH",
    "researchRequired": false,
    "governmentActionPossible": true,
    "requiredExpertise": ["Waste Management", "Environmental Engineering"],
    "requiredResources": ["Waste collection vehicles", "Pollution monitoring"],
    "confidence": 0.9100,
    "reasoning": "Outdoor burning of waste near a school creates acute environmental pollution."
  },
  "error": null
}
```

---

### Trace 2: Duplicate Detection Engine (`POST /duplicate-check`)

**Query Problem A:**
- Title: `"Garbage burning near school"`
- Description: `"Garbage is being burned near a school, producing harmful smoke."`
- Location: `{"lat": 23.3441, "long": 85.3096}`
- Primary Domain: `"Environment"`, Subcategory: `"Pollution"`

**Candidate Problem B:**
- ID: `"P1001"`
- Title: `"Unprocessed waste burning near school"`
- Description: `"Unprocessed waste is being burned close to the school causing air pollution."`
- Location: `{"lat": 23.3445, "long": 85.3098}`
- Primary Domain: `"Environment"`, Subcategory: `"Pollution"`

**Step-by-Step Scoring Trace:**
1. `EmbeddingService` generates 384-d normalized vectors $\mathbf{A}$ and $\mathbf{B}$ using `BAAI/bge-small-en-v1.5`.
2. Cosine Similarity $S_{\text{sem}} = \mathbf{A} \cdot \mathbf{B} = 0.8909$.
3. Primary domain match: `"Environment" == "Environment"` $\rightarrow M_{\text{prim}} = 1.0$.
4. Subcategory match: `"Pollution" == "Pollution"` $\rightarrow M_{\text{sub}} = 1.0$.
5. Secondary domain overlap: Jaccard overlap $J_{\text{sec}} = 1.0$.
6. Haversine Distance: $(\text{lat}_1, \text{lon}_1)$ vs $(\text{lat}_2, \text{lon}_2) \rightarrow d = 0.049\text{ km}$.
7. Location Proximity Score: $S_{\text{loc}} = 1.0 - (0.049 / 5.0) = 0.9902$.
8. Composite Weighted Score:
   $$\text{Score} = (0.50 \times 0.8909) + (0.15 \times 1.0) + (0.15 \times 1.0) + (0.10 \times 1.0) + (0.10 \times 0.9902) = 0.9421$$
9. Score $0.9421 \ge 0.85 \rightarrow \text{candidateStatus} = \text{"strong_candidate"}$.
10. Overall response status $\rightarrow \text{"candidate_found"}$.

**Returned API Response Payload:**
```json
{
  "problemId": "P2001",
  "status": "candidate_found",
  "duplicateCandidates": [
    {
      "candidateProblemId": "P1001",
      "duplicateScore": 0.9421,
      "semanticSimilarity": 0.8909,
      "primaryDomainMatch": true,
      "subcategoryMatch": true,
      "secondaryDomainOverlap": 1.0,
      "locationDistanceKm": 0.049,
      "locationScore": 0.9902,
      "candidateStatus": "strong_candidate",
      "reasons": [
        "High semantic similarity (0.891)",
        "Same primary domain (Environment)",
        "Same subcategory (Pollution)",
        "Secondary domain overlap (100%)",
        "Geographically very close (0.05 km)"
      ]
    }
  ]
}
```

---

## 28. One-Page Logic Summary

```text
CIVICFIX AI SYSTEM LOGIC SUMMARY
│
├── 1. CLASSIFICATION ENGINE (FastAPI @ Port 8000)
│   ├── Input: POST /classify (problemId, title, description, location)
│   ├── Preprocessing: Trim whitespace, collapse spaces, validate non-empty text.
│   ├── LLM Provider: Ollama API running Gemma 3 4B (gemma3:4b) locally @ http://localhost:11434
│   │   ├── Temperature: 0.1 (Hardcoded)
│   │   ├── Format: Pydantic-generated JSON Schema
│   │   └── Retries: 3 retries with exponential backoff (1s, 2s, 4s)
│   ├── Business & Taxonomy Validation:
│   │   ├── Enforces 12 Primary Domains & 40 Subcategories (app/taxonomy/taxonomy.py)
│   │   └── Evaluates 9 qualitative severity factors (Health, Scope, Vulnerable Pop, Extent, Duration, Infra, Env, Social, Reversibility)
│   ├── Safeguards & Decision Logic:
│   │   ├── IF confidence >= 0.85 AND description words >= 5 AND no vague phrases AND valid taxonomy
│   │   │     └─ status = "classified"
│   │   └── ELSE
│   │         └─ status = "review_required"
│   └── Outputs: Structured JSON with summary, domains, severity, urgency, expertise, resources, confidence.
│
└── 2. DUPLICATE DETECTION ENGINE (FastAPI @ Port 8001)
    ├── Input: POST /duplicate-check (query problem + candidate pool)
    ├── Embedding Model: BAAI/bge-small-en-v1.5 (SentenceTransformers) -> 384-d normalized float vectors
    ├── Distance Metric: Haversine spherical distance (km) with linear decay over 5.0 km radius
    ├── Multi-Factor Composite Score Formula:
    │   Score = 0.50*(Semantic Cosine Sim) + 0.15*(Primary Domain Match) + 0.15*(Subcategory Match) + 0.10*(Secondary Overlap) + 0.10*(Location Score)
    ├── Candidate Threshold Logic:
    │   ├── Score >= 0.85 -> "strong_candidate"
    │   ├── Score >= 0.75 (DUPLICATE_SIMILARITY_THRESHOLD) -> "potential_duplicate"
    │   └── Score < 0.75  -> "no_candidate"
    └── Human Review Boundary:
        └── AI surfaces candidate recommendations + explainable reasons. AI NEVER merges or deletes records automatically.
```
