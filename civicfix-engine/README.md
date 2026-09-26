# CivicFix Engine

Unified FastAPI module integrating three independently developed features into one functional backend:

| Feature | Capability |
|---|---|
| **Classification Engine** | AI-powered classification of citizen-reported societal problems |
| **Duplicate Detection Engine** | Available-signal normalized composite scoring for duplicate detection |
| **University Matching & Marketplace** | 7-factor capability matching, sequential assignment, industry marketplace |

---

## Problem → AI → Match → Assign

```
Citizen Problem Submission
        ↓
AI Classification Engine (Gemma 3 4B via Ollama)
        ↓
Duplicate Detection (BGE-small embeddings + Haversine + taxonomy signals)
        ↓
University Matching (7-factor deterministic scorer)
        ↓
Sequential University Assignment Chain
        ↓
Industry Marketplace & Collaboration
```

All three stages are internally callable Python services — **no inter-service HTTP calls**.

---

## Folder Structure

```
civicfix-engine/
├── app/
│   ├── main.py                          # FastAPI app entry point
│   ├── config.py                        # Unified Pydantic Settings
│   ├── api/
│   │   └── v1/
│   │       ├── classification.py        # POST /api/v1/classify
│   │       ├── duplicate_detection.py   # POST /api/v1/duplicate-detection/check
│   │       ├── university_matching.py   # Matching, assignment, marketplace, collaboration
│   │       └── health.py               # GET /health
│   ├── core/
│   │   ├── taxonomy.py                  # Controlled 12-domain taxonomy
│   │   ├── preprocessor.py             # Text sanitization & preprocessing
│   │   └── auth.py                      # JWT auth utilities
│   ├── database/
│   │   ├── connection.py               # MongoDB client (unified `civicfix` DB)
│   │   └── categorization_adapter.py   # Classification output → ProblemInput
│   └── services/
│       ├── classification/             # AI Classification Engine
│       │   ├── classifier_service.py   # Main orchestrator
│       │   ├── ollama_provider.py      # Ollama/Gemma LLM provider
│       │   ├── prompt_builder.py       # Structured prompt construction
│       │   └── confidence_service.py   # Confidence → status mapping
│       ├── duplicate_detection/        # Duplicate Detection Engine
│       │   ├── embedding_service.py    # BGE-small-en-v1.5 embeddings
│       │   ├── similarity_service.py   # Cosine similarity
│       │   ├── location_service.py     # Haversine distance
│       │   ├── fingerprint_service.py  # Contradiction detection
│       │   ├── retriever_service.py    # In-memory vector index
│       │   └── duplicate_service.py    # Main detector orchestrator
│       └── university_matching/        # University Matching & Marketplace
│           ├── matching_engine.py      # 7-factor scorer + DB entry point
│           ├── assignment_workflow.py  # Sequential assignment state machine
│           ├── ranking.py              # Top-N slice helper
│           ├── marketplace.py          # Industry marketplace (filter only)
│           ├── collaboration.py        # Interest → Accept/Reject → Collaboration
│           ├── normalization.py        # Synonym-based term normalization
│           ├── problem_input.py        # ProblemInput dataclass
│           ├── matching_config.py      # DEFAULT_WEIGHTS + DB config
│           ├── assignment_constants.py # ACTIVE_STATUSES, VALID_STATUSES
│           └── scoring/                # 7 pure scoring functions
│               ├── expertise.py        # Weight 0.35
│               ├── faculty.py          # Weight 0.20
│               ├── infrastructure.py   # Weight 0.15
│               ├── past_projects.py    # Weight 0.10
│               ├── geography.py        # Weight 0.10
│               ├── capacity.py         # Weight 0.05
│               └── industry_ecosystem.py # Weight 0.05
└── tests/
    ├── conftest.py                      # Unified mongomock fixtures
    ├── test_taxonomy.py
    ├── test_similarity.py
    ├── test_location.py
    ├── test_candidate_retriever.py
    ├── test_scoring.py                  # All 7 scoring factors
    ├── test_matching_engine.py
    ├── test_assignment_workflow.py
    ├── test_marketplace.py
    ├── test_collaboration.py
    └── test_integration.py             # End-to-end pipeline tests
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI 0.115.6 |
| LLM | Gemma 3 4B via Ollama (local inference) |
| Embeddings | BGE-small-en-v1.5 (`sentence-transformers`) |
| Database | MongoDB via PyMongo (unified `civicfix` database) |
| Test DB | mongomock 4.3.0 |
| Auth | PyJWT (shared secret, dev-mode passthrough) |
| Python | 3.13 |

---

## How to Run

### Prerequisites

1. Python 3.11+
2. MongoDB running on `localhost:27017` (or set `MONGO_URI` in `.env`)
3. Ollama running on `localhost:11434` with `gemma3:4b` pulled (only required for classification endpoint)

### Setup

```bash
cd civicfix-engine

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env
# Edit .env with your values

# Run
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests

```bash
cd civicfix-engine
python -m pytest tests -v
```

No MongoDB or Ollama required for tests — mongomock is used automatically.

---

## API Endpoints

### Classification Engine

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/classify` | Classify a citizen-reported problem |
| `GET` | `/health` | Health check |

**Request:** `POST /api/v1/classify`
```json
{
  "problemId": "PROB-001",
  "title": "Unsafe school toilets causing students to miss classes",
  "description": "The government school has severely damaged and unusable toilets..."
}
```

**Response:**
```json
{
  "problemId": "PROB-001",
  "status": "high_confidence",
  "classification": {
    "primaryDomain": "Sanitation",
    "subcategory": "Toilets",
    "secondaryDomains": ["Education"],
    "severity": "HIGH",
    "confidence": 0.91
  }
}
```

---

### Duplicate Detection Engine

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/duplicate-detection/check` | Check a problem against a candidate list |
| `POST` | `/api/v1/duplicate-detection/analyze-pair` | Analyze one problem-candidate pair |

**Request:** `POST /api/v1/duplicate-detection/check`
```json
{
  "problem": {
    "problemId": "NEW-001",
    "title": "Pothole on main road",
    "description": "There is a large pothole...",
    "primaryDomain": "Urban Infrastructure",
    "subcategory": "Roads",
    "location": {"lat": 23.34, "long": 85.31}
  },
  "candidates": [...]
}
```

---

### University Matching & Marketplace

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/matching/{problem_id}` | Run university matching |
| `GET` | `/api/v1/matching/{problem_id}` | Get latest matching result |
| `GET` | `/api/v1/universities/matches/{problem_id}` | Get top-5 universities |
| `GET` | `/api/v1/universities` | List universities |
| `POST` | `/api/v1/universities` | Register a university |
| `PUT` | `/api/v1/universities/{id}` | Update a university |
| `GET` | `/api/v1/assignments/by-problem/{id}` | Get assignments for problem |
| `POST` | `/api/v1/assignments/{id}/accept` | Accept assignment |
| `POST` | `/api/v1/assignments/{id}/reject` | Reject assignment |
| `GET` | `/api/v1/marketplace/solutions` | Browse solutions |
| `POST` | `/api/v1/marketplace/solutions` | Publish a solution |
| `POST` | `/api/v1/marketplace/{solution_id}/interest` | Express interest |
| `GET` | `/api/v1/collaborations` | List collaborations |

---

## Input / Output Contracts

### Classification Input
```json
{
  "problemId": "string (required)",
  "title": "string (required)",
  "description": "string (required)",
  "location": { "district": "string", "state": "string" }
}
```

### Matching Input (`POST /api/v1/matching/{problem_id}`)
```json
{
  "classification": {
    "primaryDomain": "Environment",
    "subcategory": "Pollution",
    "secondaryDomains": ["Healthcare"],
    "requiredExpertise": ["Environmental Management"],
    "requiredResources": ["Waste collection"],
    "researchRequired": true,
    "governmentActionPossible": true
  },
  "location": {
    "district": "Ranchi",
    "state": "Jharkhand",
    "latitude": 23.3441,
    "longitude": 85.3096
  }
}
```

---

## University Scoring Factors

| Factor | Weight | Source |
|---|---|---|
| Expertise Match | 35% | `required_expertise` vs `university.expertise + researchAreas` |
| Faculty Coverage | 20% | Available faculty expertise coverage |
| Infrastructure Match | 15% | `required_resources` vs `infrastructure + technologyCapabilities` |
| Relevant Past Projects | 10% | Domain/expertise overlap with past projects |
| Geographic Proximity | 10% | Same district=1.0, same state=0.6, other=0.2 |
| Current Capacity | 5% | Free project slots (halved if LIMITED) |
| Industry Ecosystem | 5% | Industry relationships aligned to problem domain |

---

## Duplicate Detection Scoring

Available-signal normalized composite scoring (signals with UNKNOWN state are excluded from the denominator):

| Signal | Base Weight | State |
|---|---|---|
| Semantic (embedding cosine sim) | 50% | Always AVAILABLE |
| Primary Domain Match | 15% | MATCH / MISMATCH / UNKNOWN |
| Subcategory Match | 15% | MATCH / MISMATCH / UNKNOWN |
| Secondary Domain Overlap | 10% | MATCH / MISMATCH / UNKNOWN |
| Location Distance | 10% | AVAILABLE / UNAVAILABLE |

Contradiction protection: fingerprint-based detection prevents false duplicates when problems affect the same entity but describe different issues (e.g. "hospital medicine shortage" vs "hospital electricity outage").

---

## Environment Variables

See [`.env.example`](.env.example) for the full list. Key variables:

| Variable | Default | Description |
|---|---|---|
| `MONGO_URI` | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGO_DB_NAME` | `civicfix` | Unified database name |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `gemma3:4b` | LLM model for classification |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | Embedding model |
| `DUPLICATE_SIMILARITY_THRESHOLD` | `0.75` | Minimum score for duplicate candidate |
| `DEFAULT_ASSIGNMENT_DEADLINE_HOURS` | `48` | Hours before assignment times out |

---

## Dependencies

See [`requirements.txt`](requirements.txt) for exact versions.

Core: `fastapi`, `uvicorn`, `pydantic-settings`, `pymongo`, `sentence-transformers`, `scikit-learn`, `numpy`, `httpx`, `PyJWT`

Test: `pytest`, `pytest-asyncio`, `mongomock`

---

## Testing

- **76 tests total** — all passing
- No MongoDB or Ollama required for any test (mongomock injected via conftest.py)
- Coverage: taxonomy, similarity, location, candidate retrieval, all 7 scoring factors, matching engine, assignment workflow, marketplace, collaboration, end-to-end pipeline integration

```
python -m pytest civicfix-engine/tests -v
```

---

## Git Branch

This module lives on branch `feature/merge-three-engines`. Original feature folders (`classification-engine/`, `duplicate-detection/`, `UniversityMatchingAlgo/`) are preserved intact.
