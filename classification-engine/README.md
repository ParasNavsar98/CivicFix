# CivicFix Classification Engine

Standalone AI classification microservice for citizen-reported civic and societal problems. Built with **FastAPI**, **Pydantic v2**, and **Ollama (Gemma 3 4B)**.

---

## 1. Purpose

The **CivicFix Classification Engine** is a dedicated, independent AI service designed to structure, categorize, and evaluate unstructured problem reports submitted by citizens. It converts raw natural-language titles and descriptions (e.g. *"Damaged school toilets causing students to miss classes"*) into standardized, machine-readable JSON classifications adhering to a controlled 12-domain societal taxonomy.

The service is strictly **AI-assisted**: high-confidence classifications (`confidence >= 0.85`) receive status `classified`, while lower-confidence or vague submissions receive status `review_required` to flag them for human oversight.

---

## 2. Responsibilities

The Classification Engine handles:

- **Problem Summarization**: Generating a concise 1-2 sentence structured summary (`problemSummary`).
- **Primary Domain Classification**: Assigning the core root physical cause to one of 12 controlled primary taxonomy domains (`primaryDomain`).
- **Subcategory Classification**: Selecting a valid subcategory belonging strictly to the chosen primary domain (`subcategory`).
- **Secondary Domain Classification**: Identifying evidence-supported distinct secondary issues belonging to other taxonomy domains (`secondaryDomains`).
- **Severity Assessment**: Evaluating 9 qualitative severity factors strictly from explicit submission evidence (`severityAssessment`).
- **Severity Evidence**: Extracting supporting evidence statements from the citizen report (`severityEvidence`).
- **People Affected Extraction**: Extracting explicit counts, units, and sources without converting reported units (`peopleAffected`).
- **Urgency Assessment**: Assigning overall urgency separate from severity (`urgency`).
- **Research Required Decision**: Determining if novel technology, R&D, or experimentation is needed (`researchRequired`).
- **Government Action Possible**: Assessing if public/municipal authority intervention can resolve the issue (`governmentActionPossible`).
- **Required Expertise & Resources**: Recommending technical skills and resources (`requiredExpertise`, `requiredResources`).
- **Confidence Evaluation**: Calculating a normalized score between `0.0` and `1.0` (`confidence`).
- **Reasoning**: Providing explicit justification for classification decisions (`reasoning`).
- **Taxonomy & Business Validation**: Enforcing strict schema and domain/subcategory constraints.
- **Review Decision Boundary**: Flagging vague or low-confidence reports for human review (`review_required`).

---

## 3. Architecture

```text
POST /classify (Citizen Input)
    │
    ▼
1. Pydantic Input Validation (ProblemClassificationInput)
    │
    ▼
2. Input Preprocessing & Sanitization (preprocessor.py)
    │
    ▼
3. Taxonomy-Aware Prompt Construction (build_classification_prompt)
    │
    ▼
4. LLM Execution via Ollama (Gemma 3 4B / gemma3:4b)
    │
    ▼
5. Structured JSON Parsing & Pydantic Validation (ClassificationResult)
    │
    ▼
6. Business & Taxonomy Validation (validate_taxonomy_rules)
    │
    ▼
7. Evidence-Based Secondary Domain Safeguard (extract_evidence_based_secondary_domains)
    │
    ▼
8. Evidence Sufficiency & Ambiguity Safeguards (is_evidence_sufficient, detect_ambiguity)
    │
    ▼
9. Confidence Threshold Evaluation (evaluate_confidence)
    │
    ├──────────────────────────────┐
    ▼                              ▼
High Confidence (>= 0.85)     Low Confidence (< 0.85) or Ambiguous
    │                              │
    ▼                              ▼
 status: "classified"          status: "review_required"
    └──────────────┬───────────────┘
                   ▼
       JSON Response (ClassificationResponse)
```

---

## 4. Project Structure

```text
classification-engine/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI entry point, exception handlers & routing
│   ├── config.py                # Centralized Pydantic configuration settings
│   │
│   ├── schemas/                 # Data contracts & validation models
│   │   ├── __init__.py
│   │   ├── input.py             # Citizen submission input schema
│   │   └── classification.py    # Structured result & response schemas
│   │
│   ├── services/                # Core business & evaluation logic
│   │   ├── __init__.py
│   │   ├── preprocessor.py      # Input sanitization & normalization
│   │   ├── classifier.py        # Pipeline orchestrator & taxonomy validator
│   │   └── confidence.py        # Confidence thresholding & status evaluator
│   │
│   ├── ai/                      # LLM Provider integrations
│   │   ├── __init__.py
│   │   ├── provider.py          # Abstract LLMProvider interface & exception hierarchy
│   │   ├── ollama.py            # Local Ollama HTTP client implementation
│   │   └── prompts.py           # Dynamic prompt builder embedding 12-domain taxonomy
│   │
│   └── taxonomy/                # Controlled domain taxonomy definition
│       ├── __init__.py
│       └── taxonomy.py          # 12 primary domains, subcategories & validator functions
│
├── tests/                       # Automated unit, integration & evaluation suite
│   ├── evaluation_dataset.json  # 50-item ground-truth test dataset
│   ├── test_api.py              # FastAPI endpoint tests
│   ├── test_classifier.py       # Classifier service & regression tests (Cases 1-5)
│   ├── test_confidence.py       # Confidence threshold tests
│   ├── test_ollama.py           # Ollama provider retry & timeout tests
│   ├── test_precision_and_metrics.py # Benchmark metrics evaluation
│   ├── test_schemas.py          # Pydantic schema validation tests
│   ├── test_security.py         # Prompt injection & input sanitization tests
│   ├── test_severity_assessment.py # 9-factor severity framework tests
│   └── test_taxonomy.py         # Taxonomy domain/subcategory validation tests
│
├── .env.example                 # Environment configuration template
├── .gitignore                   # Git ignore file
├── requirements.txt             # Python dependencies
└── README.md                    # Component documentation
```

---

## 5. Requirements

- **Python**: 3.11 or higher
- **Ollama**: Local inference engine ([ollama.com](https://ollama.com))
- **Model**: Gemma 3 4B (`gemma3:4b`)

---

## 6. Installation

1. **Clone/Navigate to Component**:
   ```bash
   cd classification-engine
   ```

2. **Create and Activate Virtual Environment**:
   ```powershell
   # Windows PowerShell:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux/macOS:
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Pull Gemma 3 4B Model via Ollama**:
   ```bash
   ollama pull gemma3:4b
   ```

---

## 7. Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Configurable parameters (`app/config.py`):

| Variable | Default Value | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Base URL of local Ollama server |
| `OLLAMA_MODEL` | `gemma3:4b` | Ollama model identifier |
| `LLM_TIMEOUT_SECONDS` | `60.0` | HTTP timeout per request in seconds |
| `LLM_MAX_RETRIES` | `3` | Exponential backoff retry attempts |
| `AI_HIGH_CONFIDENCE_THRESHOLD` | `0.85` | Minimum confidence for `classified` status |
| `AI_REVIEW_THRESHOLD` | `0.60` | Minimum threshold for review boundary |

---

## 8. Running Independently

Start the service locally on **Port 8000**:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- **Interactive API Documentation (Swagger UI)**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 9. API Specifications

### 9.1 GET `/health`
Health probe for service monitoring.

**Response**:
```json
{
  "status": "healthy"
}
```

---

### 9.2 POST `/classify`
Main classification endpoint. Accepts citizen report JSON and returns structured classification.

#### Request Contract (`ProblemClassificationInput`)
```json
{
  "problemId": "P1001",
  "title": "Unsafe school toilets causing students to miss classes",
  "description": "The government school has severely damaged and unusable toilets. Students are frequently unable to attend classes because there are no functional sanitation facilities. The problem creates both a sanitation failure and a direct education access problem.",
  "location": {
    "district": "Ranchi",
    "state": "Jharkhand",
    "latitude": 23.3441,
    "longitude": 85.3096
  }
}
```

#### Successful Response Contract (`ClassificationResponse` — `classified`)
```json
{
  "problemId": "P1001",
  "status": "classified",
  "classification": {
    "problemSummary": "Damaged school toilets are preventing students from attending classes, creating a direct impact on education access.",
    "primaryDomain": "Sanitation",
    "secondaryDomains": [
      "Education"
    ],
    "subcategory": "Toilets",
    "severity": "CRITICAL",
    "severityAssessment": {
      "healthSafetyImpact": "HIGH",
      "exposureScope": "COMMUNITY",
      "vulnerablePopulationExposure": "CLEAR",
      "geographicExtent": "LOCAL_AREA",
      "duration": "ONGOING",
      "infrastructureImpact": "CRITICAL",
      "environmentalImpact": "NONE",
      "socialEconomicImpact": "HIGH",
      "reversibility": "DIFFICULT_TO_RECOVER"
    },
    "severityEvidence": [
      "Government school has severely damaged and unusable toilets.",
      "Students are frequently unable to attend classes because there are no functional sanitation facilities."
    ],
    "peopleAffected": {
      "value": null,
      "unit": null,
      "source": "NOT_PROVIDED"
    },
    "urgency": "HIGH",
    "researchRequired": false,
    "governmentActionPossible": true,
    "requiredExpertise": [
      "Sanitation Engineering",
      "Construction Management"
    ],
    "requiredResources": [
      "Construction Materials",
      "Labor"
    ],
    "confidence": 0.95,
    "reasoning": "The core problem is unusable toilets (Sanitation/Toilets). This directly impacts student attendance and education (Education)."
  },
  "error": null
}
```

#### Low Confidence / Ambiguous Response (`review_required`)
```json
{
  "problemId": "P1002",
  "status": "review_required",
  "classification": {
    "problemSummary": "Unclear problem reported in village",
    "primaryDomain": "Other",
    "secondaryDomains": [],
    "subcategory": "Unclassified",
    "severity": "LOW",
    "severityAssessment": {
      "healthSafetyImpact": "UNKNOWN",
      "exposureScope": "UNKNOWN",
      "vulnerablePopulationExposure": "NONE_IDENTIFIED",
      "geographicExtent": "UNKNOWN",
      "duration": "UNKNOWN",
      "infrastructureImpact": "NONE",
      "environmentalImpact": "NONE",
      "socialEconomicImpact": "NONE",
      "reversibility": "UNKNOWN"
    },
    "severityEvidence": [],
    "peopleAffected": {
      "value": null,
      "unit": null,
      "source": "NOT_PROVIDED"
    },
    "urgency": "LOW",
    "researchRequired": false,
    "governmentActionPossible": false,
    "requiredExpertise": [],
    "requiredResources": [],
    "confidence": 0.40,
    "reasoning": "Input description is too vague to determine a specific domain or severity."
  },
  "error": null
}
```

#### Error Response (`failed`)
```json
{
  "problemId": "P1003",
  "status": "failed",
  "classification": null,
  "error": {
    "errorCode": "INVALID_TAXONOMY_CATEGORY",
    "message": "Invalid primary domain 'InvalidDomain'. Must be one of controlled taxonomy domains."
  }
}
```

---

## 10. Taxonomy Structure

The engine enforces a strict 12-domain taxonomy (`app/taxonomy/taxonomy.py`):

1. **Education**: `Access`, `Infrastructure`, `Learning Support`, `Digital Education`
2. **Healthcare**: `Access`, `Public Health`, `Facilities`, `Diagnostics`
3. **Agriculture**: `Irrigation`, `Crop Support`, `Storage`, `Market Linkage`
4. **Water Resources**: `Supply`, `Quality`, `Leakage`, `Conservation`, `Monitoring`
5. **Sanitation**: `Waste`, `Drainage`, `Toilets`, `Cleanliness`
6. **Environment**: `Pollution`, `Biodiversity`, `Waste Reduction`, `Climate Resilience`
7. **Energy**: `Access`, `Efficiency`, `Renewable Energy`, `Public Lighting`
8. **Urban Infrastructure**: `Roads`, `Drainage`, `Streetlights`, `Public Spaces`
9. **Accessibility**: `Mobility`, `Assistive Infrastructure`, `Inclusive Services`
10. **Public Administration**: `Service Delivery`, `Information Access`, `Process Gaps`
11. **Rural Livelihoods**: `Skills`, `Employment`, `Local Enterprises`, `Market Access`
12. **Other**: `Unclassified`

---

## 11. Secondary Domain Classification Rules

The decision rules for `secondaryDomains` strictly distinguish between distinct issues vs. indirect stakeholder exposure:

1. **Core Problem**: Primary domain is chosen based on the root physical cause/facility failure.
2. **Distinct Second Problem Requirement**: A domain is included in `secondaryDomains` **only** when there is explicit, evidence-supported text describing a distinct second problem (e.g., students missing classes -> `"Education"`).
3. **Prohibited Secondary Domain Additions**: A domain MUST NOT be added merely because:
   - An affected stakeholder is present (e.g. students or teachers at a school location),
   - The location is associated with that domain (e.g. problem occurs near a school or hospital),
   - The issue has indirect downstream consequences,
   - Or the model infers plausible relevance without explicit evidence.
4. **Decision Rule Comparison Examples**:
   - *"Unsafe school toilets causing students to miss classes"* -> `primaryDomain`: Sanitation, `subcategory`: Toilets, `secondaryDomains`: `["Education"]`. (Explicit evidence of education access failure).
   - *"Garbage burning near school"* -> `primaryDomain`: Environment, `subcategory`: Pollution, `secondaryDomains`: `[]`. (Location is near school, but no distinct education access failure is stated).
   - *"Broken school toilets"* -> `primaryDomain`: Sanitation, `subcategory`: Toilets, `secondaryDomains`: `[]`. (No mention of missed classes).

---

## 12. Severity Assessment Framework

Severity (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) is computed after systematically evaluating 9 evidence-based qualitative factors:

1. `healthSafetyImpact`: `NONE`, `LOW`, `MODERATE`, `HIGH`, `CRITICAL`, `UNKNOWN`
2. `exposureScope`: `INDIVIDUAL`, `LOCAL`, `COMMUNITY`, `LARGE_AREA`, `WIDESPREAD`, `UNKNOWN`
3. `vulnerablePopulationExposure`: `NONE_IDENTIFIED`, `POSSIBLE`, `CLEAR`, `UNKNOWN`
4. `geographicExtent`: `SINGLE_LOCATION`, `LOCAL_AREA`, `MULTIPLE_LOCATIONS`, `WIDE_AREA`, `UNKNOWN`
5. `duration`: `SHORT_TERM`, `ONGOING`, `LONG_TERM`, `PERSISTENT`, `UNKNOWN`
6. `infrastructureImpact`: `NONE`, `LOW`, `MODERATE`, `HIGH`, `CRITICAL`, `UNKNOWN`
7. `environmentalImpact`: `NONE`, `LOW`, `MODERATE`, `HIGH`, `CRITICAL`, `UNKNOWN`
8. `socialEconomicImpact`: `NONE`, `LOW`, `MODERATE`, `HIGH`, `CRITICAL`, `UNKNOWN`
9. `reversibility`: `EASILY_REVERSIBLE`, `RECOVERABLE`, `DIFFICULT_TO_RECOVER`, `POTENTIALLY_IRREVERSIBLE`, `UNKNOWN`

---

## 13. Testing

Run the automated test suite with `pytest`:

```bash
python -m pytest classification-engine/tests
```

**Verified Test Results**:
- **Total Tests**: 70 Passed, 0 Failed
- **Execution Time**: ~6 seconds

---

## 14. Integration Into Another Repository

To integrate the Classification Engine into another platform or backend:

1. Treat the engine as an independent HTTP microservice over REST.
2. Send a `POST http://<host>:8000/classify` request during problem creation or submission pipelines.
3. The consuming application backend processes the JSON response and stores the resulting classification fields in its own database.

```text
Consuming Platform Backend
          │
          ▼ POST http://localhost:8000/classify
Classification Engine Service (:8000)
          │
          ▼ Returns ClassificationResponse JSON
Consuming Platform Backend stores result in local DB
```

### Python Integration Example
```python
import httpx

async def classify_submission(title: str, description: str, district: str, state: str):
    payload = {
        "problemId": "PROB-001",
        "title": title,
        "description": description,
        "location": {"district": district, "state": state}
    }
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/classify", json=payload)
        response.raise_for_status()
        return response.json()
```

---

## 15. Integration Checklist

- [ ] Install and verify Ollama (`ollama --version`)
- [ ] Pull Gemma 3 4B model (`ollama pull gemma3:4b`)
- [ ] Copy `.env.example` to `.env` and verify port 8000 configuration
- [ ] Launch service: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [ ] Verify `GET http://localhost:8000/health` returns `{"status": "healthy"}`
- [ ] Configure consuming backend `VITE_CLASSIFICATION_URL` / `CLASSIFICATION_ENGINE_URL` to `http://localhost:8000`
- [ ] Call `POST /classify` and handle `classified`, `review_required`, and `failed` status outcomes

---

## 16. What NOT to Copy

When extracting or integrating this component into another repository, **DO NOT**:
- Copy or import internal Python modules (`app.services`, `app.ai`) directly into your application code.
- Tie your domain models directly to internal Pydantic schemas; depend only on the HTTP REST API contract.
- Hardcode LLM provider logic or Ollama API calls inside your core backend application.
