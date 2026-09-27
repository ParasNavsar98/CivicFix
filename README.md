# CivicFix — Societal Problem-to-Solution Orchestration Platform

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-76%2F76%20Passing-brightgreen.svg)]()

> **CivicFix** is an open-source, AI-assisted platform that transforms citizen-reported societal problems into structured, actionable workflows involving citizens, human reviewers, government departments, research institutions, universities, and industry collaborators.

---

## Executive Summary

CivicFix is **not simply a complaint portal**. It is an end-to-end problem-to-solution orchestration system.

```
CAPTURE ──► UNDERSTAND ──► VALIDATE ──► ROUTE ──► MATCH ──► COLLABORATE ──► IMPLEMENT ──► MEASURE
```

In traditional civic portals, citizen issues often stall in unmonitored queues or lack technical pathways toward resolution. CivicFix solves this by combining local AI inference (Gemma 3 4B via Ollama), semantic duplicate detection (BGE-small), 7-factor university capability matching, and an industry marketplace into a **unified FastAPI backend engine** (`civicfix-engine/`).

> [!IMPORTANT]
> **Human-in-the-Loop Principle**: AI assists decision-making by surfacing structured classifications, severity assessments, duplicate candidate signals, and capability scores. **All consequential decisions**—such as duplicate merges, category corrections, government routing, and university assignments—remain strictly under authorized human control.

---

## Key Achievements & Recent Updates

- **Unified Backend Engine (`civicfix-engine/`)**: Consolidated three standalone AI microservices (Classification, Duplicate Detection, and University Matching) into a single, high-performance FastAPI module (`ac2dc64`).
- **Zero Inter-Service HTTP Overhead**: All three engines run as internal Python services, eliminating internal HTTP latency and network failure modes during core intake and routing.
- **Unified Data Layer**: Single MongoDB database (`civicfix`) with automated index management.
- **Comprehensive Verification**: 76 unit and integration tests passing in `civicfix-engine/tests/` (plus 163 original baseline tests preserved across individual feature directories, totaling **239 tests**).

---

## Core Lifecycle Flow

```mermaid
flowchart TD
    subgraph Capture & Intake
        A["Citizen / Submitter"] -->|Submits Problem| B["CivicFix Platform Intake"]
        B -->|Store Problem FIRST| DB[("MongoDB (civicfix)")]
    end

    subgraph Integrated AI Engine (civicfix-engine)
        B --> C["AI Classification Engine\n(Gemma 3 4B via Ollama)"]
        C --> D["Taxonomy, Severity, Urgency &\nRouting Flags"]
        
        B --> E["Duplicate Detection Engine\n(BGE-small + Haversine + Fingerprint)"]
        E --> F["Duplicate Candidates &\nScore Breakdown"]

        D --> G{"Workflow Engine"}
        F --> G
    end

    subgraph Human Validation Boundary
        G -->|"Low Confidence (<0.85) OR\nDuplicate Candidate Found"| H["Reviewer Queue\n(Human-in-the-Loop)"]
        H -->|Accept / Correct / Merge| I["Validated Problem"]
        G -->|"High Confidence (>=0.85) &\nUnique"| I
    end

    subgraph Routing & Matching
        I --> J{"Routing Decision"}
        J -->|Government Action| K["Government Department Routing"]
        J -->|Research / Innovation| L["University Matching Engine\n(7-Factor Deterministic Scorer)"]
        
        L --> M["Ranked Universities (Top 5)"]
        M --> N["Sequential Assignment Workflow\n(PENDING -> SENT -> ACCEPTED/REJECTED)"]
        N -->|Accepted| O["Industry Marketplace &\nCollaboration Portal"]
    end
```

---

## Integrated AI & Matching Engines

The core intelligence of CivicFix is housed in `civicfix-engine/app/services/` as three integrated Python service modules:

```
civicfix-engine/app/services/
├── classification/          # AI Classification Engine (Gemma 3 4B via Ollama)
├── duplicate_detection/     # Duplicate Detection Engine (BGE-small + Haversine)
└── university_matching/     # 7-Factor University Matching & Marketplace
```

---

### 1. AI Classification Engine

- **Technology**: FastAPI, Pydantic v2, Ollama, `gemma3:4b`
- **Execution Mode**: Direct internal Python service calls (`ClassifierService`)
- **Primary Function**: Analyzes raw citizen text to generate structured taxonomy classification, severity ratings, urgency, required expertise, and routing recommendation flags.

#### Controlled 12-Domain Taxonomy
Classification is strictly enforced against a controlled taxonomy defined in [`app/core/taxonomy.py`](file:///d:/CivicFix/civicfix-engine/app/core/taxonomy.py):

| Primary Domain | Subcategories |
|---|---|
| **Education** | Access, Infrastructure, Learning Support, Digital Education |
| **Healthcare** | Access, Public Health, Facilities, Diagnostics |
| **Agriculture** | Irrigation, Crop Support, Storage, Market Linkage |
| **Water Resources** | Supply, Quality, Leakage, Conservation, Monitoring |
| **Sanitation** | Waste, Drainage, Toilets, Cleanliness |
| **Environment** | Pollution, Biodiversity, Waste Reduction, Climate Resilience |
| **Energy** | Access, Efficiency, Renewable Energy, Public Lighting |
| **Urban Infrastructure** | Roads, Drainage, Streetlights, Public Spaces |
| **Accessibility** | Mobility, Assistive Infrastructure, Inclusive Services |
| **Public Administration** | Service Delivery, Information Access, Process Gaps |
| **Rural Livelihoods** | Skills, Employment, Local Enterprises, Market Access |
| **Other** | Unclassified |

#### Output Safeguards & Secondary Domains
- **Evidence-Based Secondary Domain Extraction**: Automatically surfaces cross-cutting issues (e.g., damaged school toilets triggering `Sanitation` as primary and `Education` as secondary).
- **Confidence Evaluation**:
  - `high_confidence` ($\ge 0.85$): Auto-validates if no duplicate is found.
  - `needs_review` ($0.60 \le c < 0.85$ or ambiguity/vague text): Routes to human reviewer queue.
  - `failed`: System fallback triggered on AI exception without losing submission data.

---

### 2. Duplicate Detection Engine

- **Technology**: `sentence-transformers`, `BAAI/bge-small-en-v1.5` (384-dim), Haversine distance, Scikit-learn
- **Execution Mode**: Direct internal Python service calls (`DuplicateDetector`)
- **Scoring Version**: `duplicate-v2` (Available-Signal Normalized Composite Scoring)

#### Multi-Signal Weighting Framework
Signals missing from a candidate record (e.g. unprovided location or secondary domains) are treated as `UNKNOWN`/`UNAVAILABLE` and excluded from the denominator to ensure fair scoring:

| Signal | Base Weight | Signal States | Description |
|---|---|---|---|
| **Semantic Similarity** | **50%** | Always AVAILABLE | Cosine similarity between 384-dimensional BGE-small dense embeddings |
| **Primary Domain Match** | **15%** | MATCH / MISMATCH / UNKNOWN | Binary domain match comparison |
| **Subcategory Match** | **15%** | MATCH / MISMATCH / UNKNOWN | Binary subcategory match comparison |
| **Secondary Domain Overlap**| **10%** | MATCH / MISMATCH / UNKNOWN | Jaccard overlap index of secondary domain lists |
| **Location Proximity** | **10%** | AVAILABLE / UNAVAILABLE | Haversine distance scored against a 5.0 km radius threshold |

#### Fingerprint & Contradiction Protection
Uses [`ProblemFingerprintService`](file:///d:/CivicFix/civicfix-engine/app/services/duplicate_detection/fingerprint_service.py) to prevent false positives when two problems affect the same facility but describe distinct failure modes (e.g., "Hospital medicine shortage" vs. "Hospital power outage").

#### Decision Thresholds
- `STRONG_CANDIDATE_THRESHOLD`: $\ge 0.85$
- `DUPLICATE_SIMILARITY_THRESHOLD`: $\ge 0.75$
- `SEMANTIC_STRONG_THRESHOLD`: $\ge 0.82$

> **Human Control**: Duplicate detection returns ranked candidate recommendations with explainable signal breakdowns (`scoreBreakdown`). Final merge operations (`MERGE_DUPLICATE`) must be executed by a human reviewer.

---

### 3. University Matching Engine & Marketplace

- **Technology**: Deterministic 7-Factor Weighted Scorer, Sequential State Machine
- **Execution Mode**: Direct internal Python service calls (`run_matching_for_problem`, `create_assignment_chain`)

#### 7-Factor Scoring Formula
Scores university capability ($0 - 100$) against a validated problem using explicit, configurable weights (`DEFAULT_WEIGHTS`):

$$\text{FinalScore} = \sum_{i=1}^{7} \left( \text{FactorScore}_i \times \text{Weight}_i \right) \times 100$$

| Factor | Weight | Evaluation Criteria |
|---|---|---|
| **Expertise Match** | **35%** | Exact/synonym overlap between `required_expertise` and university expertise/research areas |
| **Faculty Coverage** | **20%** | Proportion of required expertise covered by available faculty members |
| **Infrastructure Match** | **15%** | Overlap between `required_resources` and university labs/tech capabilities |
| **Relevant Past Projects** | **10%** | Past university project domain/expertise overlap (normalized by divisor $= 2$) |
| **Geographic Proximity** | **10%** | Same district $= 1.0$, same state $= 0.6$, different state $= 0.2$ |
| **Current Capacity** | **5%** | Ratio of available project slots (discounted by 50% if availability status is `LIMITED`) |
| **Industry Ecosystem** | **5%** | Presence of industry partnerships aligned with the problem's primary domain |

#### Sequential Assignment Workflow
Candidate universities are ranked deterministically (FinalScore desc, ExpertiseScore desc, UniversityID asc). Top-5 candidates enter a sequential assignment chain:

```
PENDING ──► SENT (Rank 1) ──► ACCEPTED (Triggers handoff, cancels ranks 2-5)
               │
               ├──► REJECTED (Activates Rank 2 SENT)
               └──► TIMED_OUT (Default 48h deadline; activates Rank 2 SENT)
```

#### Industry Marketplace & Collaboration
Published university solutions can be searched by domain, state, district, development stage (`IDEA`, `PROTOTYPE`, `PILOT`, `DEPLOYED`), support needed, and partner type. Industry partners express interest (`express_interest`), which university owners accept (`accept_interest`) or reject with feedback.

---

## Technology Stack

| Layer | Technology | Version / Specification |
|---|---|---|
| **Language** | Python | 3.11+ (Tested on Python 3.13) |
| **API Framework** | FastAPI | `0.115.6` |
| **ASGI Server** | Uvicorn | `0.34.0` |
| **Data Validation** | Pydantic / Pydantic Settings | `2.10.4` / `2.7.1` |
| **AI LLM Engine** | Ollama / Gemma 3 | `gemma3:4b` (4 Billion parameters) |
| **Embedding Engine** | Sentence Transformers | `BAAI/bge-small-en-v1.5` (384 dimensions) |
| **Machine Learning** | Scikit-learn / NumPy | `1.7.2` / `2.3.3` |
| **Database** | MongoDB | PyMongo `4.13.2` |
| **Database Mocking**| mongomock | `4.3.0` |
| **Frontend QA Console**| React, Vite, TypeScript, Tailwind CSS | React 19, Vite 8, Tailwind v4 |

---

## Unified Repository Structure

```text
CivicFix/
├── civicfix-engine/                      # UNIFIED ACTIVE BACKEND ENGINE
│   ├── app/
│   │   ├── main.py                       # FastAPI application entry point & lifespan
│   │   ├── config.py                     # Unified Pydantic Settings
│   │   ├── api/
│   │   │   └── v1/                       # Versioned API Routes
│   │   │       ├── classification.py     # POST /api/v1/classify
│   │   │       ├── duplicate_detection.py# POST /api/v1/duplicate-detection/check
│   │   │       ├── university_matching.py# Matching, assignment, marketplace, collab
│   │   │       └── health.py            # GET /health & GET /api/v1/health
│   │   ├── core/
│   │   │   ├── taxonomy.py               # Controlled 12-domain taxonomy
│   │   │   ├── preprocessor.py          # Text sanitization & preprocessing
│   │   │   └── auth.py                   # JWT auth utilities
│   │   ├── database/
│   │   │   ├── connection.py            # MongoDB connection & index creation (`civicfix`)
│   │   │   └── categorization_adapter.py# Adapter between classification JSON & ProblemInput
│   │   └── services/
│   │       ├── classification/          # Internal AI Classifier Service
│   │       ├── duplicate_detection/     # Internal Duplicate Detector Service
│   │       └── university_matching/     # Internal 7-Factor Scorer & Workflow
│   ├── tests/                           # Unified Test Suite (76 passing tests)
│   ├── requirements.txt                 # Pinned dependencies
│   ├── .env.example                     # Environment template
│   └── README.md                        # Module documentation
│
├── testing-console/                      # DEVELOPER QA FRONTEND (React 19 + Vite)
│   ├── src/                             # 14 QA testing views
│   ├── package.json
│   └── README.md
│
├── backend/                              # Main Workflow Orchestrator (Legacy/Standalone)
├── integration-tests/                    # Integration test fixtures
├── classification-engine/                # Original standalone classification codebase (Preserved)
├── duplicate-detection/                  # Original standalone duplicate codebase (Preserved)
├── UniversityMatchingAlgo/               # Original standalone matching codebase (Preserved)
├── INTEGRATION_GUIDE.md                  # Integration specification guide
└── REPOSITORY_INTEGRATION_ANALYSIS.md    # Initial technical audit report
```

---

## Unified API Endpoints

All active backend endpoints are hosted on `civicfix-engine` (`http://localhost:8000`):

### 1. Health Checks
| Method | Path | Summary |
|---|---|---|
| `GET` | `/health` | Unversioned health probe |
| `GET` | `/api/v1/health` | Versioned health status (`status: healthy`) |

### 2. AI Classification Engine
| Method | Path | Summary | Request Body |
|---|---|---|---|
| `POST` | `/api/v1/classify` | Classify citizen problem | `ProblemClassificationInput` (`problemId`, `title`, `description`) |

### 3. Duplicate Detection Engine
| Method | Path | Summary | Request Body |
|---|---|---|---|
| `POST` | `/api/v1/duplicate-detection/check` | Check duplicate candidates | `problem`, `candidates`, `top_k` (default 10) |
| `POST` | `/api/v1/duplicate-detection/analyze-pair` | Analyze single pair | `problem`, `candidate` |

### 4. University Matching Engine
| Method | Path | Summary | Request / Query |
|---|---|---|---|
| `POST` | `/api/v1/matching/{problem_id}` | Run 7-factor matching | `classification` JSON, `location` (`district`, `state`) |
| `GET` | `/api/v1/matching/{problem_id}` | Get latest matching result | Path parameter `problem_id` |
| `GET` | `/api/v1/universities/matches/{problem_id}` | Get top-5 university matches | Path parameter `problem_id` |

### 5. University Management
| Method | Path | Summary |
|---|---|---|
| `GET` | `/api/v1/universities` | List all universities (optional `status` query filter) |
| `GET` | `/api/v1/universities/{university_id}` | Get university details by ID |
| `POST` | `/api/v1/universities` | Register a new university record |
| `PUT` | `/api/v1/universities/{university_id}` | Update university capabilities / capacity |

### 6. Assignment Workflow
| Method | Path | Summary |
|---|---|---|
| `GET` | `/api/v1/assignments/by-problem/{problem_id}` | List assignment chain for problem |
| `GET` | `/api/v1/assignments/{assignment_id}` | Get assignment status (evaluates timeout lazily) |
| `POST` | `/api/v1/assignments/{assignment_id}/accept` | Accept assignment (cancels pending siblings) |
| `POST` | `/api/v1/assignments/{assignment_id}/reject` | Reject assignment with reason (activates next rank) |

### 7. Industry Marketplace & Collaboration
| Method | Path | Summary |
|---|---|---|
| `GET` | `/api/v1/marketplace/solutions` | Search published solutions with domain/location filters |
| `POST` | `/api/v1/marketplace/solutions` | Publish a solution to marketplace |
| `GET` | `/api/v1/marketplace/solutions/{solution_id}` | Get solution details |
| `POST` | `/api/v1/marketplace/{solution_id}/interest` | Express industry partner interest |
| `GET` | `/api/v1/solutions/{solution_id}/interests` | List partner interests for a solution |
| `POST` | `/api/v1/interests/{interest_id}/accept` | Accept interest (creates active collaboration) |
| `POST` | `/api/v1/interests/{interest_id}/reject` | Reject interest with feedback |
| `GET` | `/api/v1/collaborations` | List active industry collaborations |

---

## Database Architecture (MongoDB)

CivicFix uses a single, unified MongoDB database named `civicfix`.

### Database Collections & Indexes
Indexes are automatically created on startup via `ensure_indexes()` in [`app/database/connection.py`](file:///d:/CivicFix/civicfix-engine/app/database/connection.py):

| Collection | Purpose | Indexed Fields |
|---|---|---|
| `universities` | University profiles, capabilities, faculty, capacity | `universityId` (Unique), `institution.location.district`, `institution.location.state`, `expertise`, `status` |
| `solutions` | Published marketplace solutions | `domain`, `subcategory`, `location.state`, `location.district`, `developmentStage`, `supportNeeded`, `partnerType`, `status`, `visibility` |
| `university_assignments` | Sequential assignment state records | `assignmentId` (Unique), `problemId`, `status` |
| `industry_interests` | Partner expressions of interest | `solutionId`, `status` |
| `matching_results` | Historical ranked matching outputs | `problemId` |
| `matching_configuration` | Configurable scoring weights | `configId` (Unique) |

> [!CAUTION]
> **Environment Protection**: Never commit real database credentials or URI strings to Git. Use placeholders in documentation and store secrets strictly in local `.env` files.

---

## Environment Variables

All settings are configured via `civicfix-engine/.env`:

| Variable | Default Value | Description |
|---|---|---|
| `APP_TITLE` | `CivicFix Integrated AI Engine & Capability Portal` | FastAPI title |
| `HOST` | `0.0.0.0` | Bind host address |
| `PORT` | `8000` | Server port |
| `MONGO_URI` | `mongodb://localhost:27017` | MongoDB connection URI (or MongoDB Atlas string) |
| `MONGO_DB_NAME` | `civicfix` | Target database name |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama service base URL |
| `OLLAMA_MODEL` | `gemma3:4b` | Ollama model identifier |
| `LLM_TIMEOUT_SECONDS` | `60.0` | Maximum timeout for LLM inference |
| `AI_HIGH_CONFIDENCE_THRESHOLD` | `0.85` | Threshold for automatic validation |
| `AI_REVIEW_THRESHOLD` | `0.60` | Threshold below which review is required |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | HuggingFace embedding model name |
| `EMBEDDING_DIMENSION` | `384` | Dense vector dimension size |
| `DUPLICATE_SIMILARITY_THRESHOLD` | `0.75` | Base duplicate threshold |
| `SEMANTIC_WEIGHT` | `0.50` | Semantic similarity weight in duplicate scoring |
| `PRIMARY_DOMAIN_WEIGHT` | `0.15` | Primary domain match weight |
| `SUBCATEGORY_WEIGHT` | `0.15` | Subcategory match weight |
| `SECONDARY_DOMAIN_WEIGHT` | `0.10` | Secondary domain match weight |
| `LOCATION_WEIGHT` | `0.10` | Location proximity weight |
| `DEFAULT_ASSIGNMENT_DEADLINE_HOURS` | `48` | Hours before rank assignment times out |

---

## Prerequisites & Installation

### System Prerequisites
1. **Python**: Python `3.11` or higher installed.
2. **MongoDB**: Local MongoDB instance (`localhost:27017`) OR MongoDB Atlas cluster URI.
3. **Ollama**: Local Ollama server (`http://localhost:11434`) with model `gemma3:4b` pulled (only required for live AI classification endpoint execution).

### Step-by-Step Windows Installation

```powershell
# 1. Navigate to the unified engine directory
cd D:\CivicFix\civicfix-engine

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create local environment configuration
copy .env.example .env
# Open .env and adjust MONGO_URI or OLLAMA_BASE_URL if required

# 6. Pull Ollama Gemma 3 4B Model (in a separate terminal)
ollama pull gemma3:4b
```

---

## Running the Backend

Start the unified server with Uvicorn:

```powershell
cd D:\CivicFix\civicfix-engine
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once running, access:
- **Root Info**: [http://localhost:8000/](http://localhost:8000/)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc API Spec**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## Running the QA Testing Console (UI)

CivicFix includes a developer QA and observation console built with React 19 and Vite (`testing-console/`):

```powershell
cd D:\CivicFix\testing-console
npm install
npm run dev
```

Open [http://localhost:5173/](http://localhost:5173/) in your browser to access 14 interactive QA test benches, including microservice health monitors, real problem submission forms, AI classification labs, duplicate comparators, reviewer action benches, and audit trail viewers.

---

## Testing & Verification

CivicFix contains an extensive test suite verifying logic across unit, module, and integration boundaries.

### Run Unified Engine Test Suite (76 Tests)

```powershell
cd D:\CivicFix\civicfix-engine
python -m pytest tests -v
```

> **Note**: Tests run automatically using `mongomock` in memory. No active MongoDB instance or Ollama server is required to execute tests.

### Current Test Summary

| Test Suite Directory | Test File | Category | Count | Status |
|---|---|---|---|---|
| `civicfix-engine/tests/` | `test_taxonomy.py` | Taxonomy domain validation | 4 | **PASS** |
| `civicfix-engine/tests/` | `test_similarity.py` | Cosine similarity & vector logic | 8 | **PASS** |
| `civicfix-engine/tests/` | `test_location.py` | Haversine distance & location scoring | 5 | **PASS** |
| `civicfix-engine/tests/` | `test_candidate_retriever.py` | In-memory candidate retrieval | 4 | **PASS** |
| `civicfix-engine/tests/` | `test_scoring.py` | 7-Factor University Scorers | 20 | **PASS** |
| `civicfix-engine/tests/` | `test_matching_engine.py` | Weighted scoring & persistence | 3 | **PASS** |
| `civicfix-engine/tests/` | `test_assignment_workflow.py` | Assignment chain state machine | 9 | **PASS** |
| `civicfix-engine/tests/` | `test_marketplace.py` | Solution search & filtering | 6 | **PASS** |
| `civicfix-engine/tests/` | `test_collaboration.py` | Express interest & accept/reject | 8 | **PASS** |
| `civicfix-engine/tests/` | `test_integration.py` | Pipeline integration & fingerprints | 9 | **PASS** |
| **Unified Total** | | | **76 / 76** | **PASSING** |
| **Baseline Feature Folders** | `classification-engine`, `duplicate-detection`, `UniversityMatchingAlgo` | Original standalone unit suites | **163** | **PASSING** |
| **Grand Total** | | | **239** | **PASSING** |

---

## Live Integration Verification

The following live integrations have been verified empirically in active sessions:

1. **FastAPI Application Lifecycle**: Startup event triggers database client initialization and creates MongoDB collection indexes (`ensure_indexes`).
2. **MongoDB Atlas & Local Connectivity**: Successfully connects to local MongoDB or Atlas clusters via `MONGO_URI`.
3. **Classification API (`POST /api/v1/classify`)**: Accepts raw problem JSON, preprocesses text, invokes Ollama (`gemma3:4b`), enforces taxonomy constraints, extracts evidence-supported secondary domains, and outputs valid `ClassificationResponse`.
4. **Duplicate Detection API (`POST /api/v1/duplicate-detection/check`)**: Calculates 384-dimensional BGE-small embeddings, evaluates Haversine distance, checks fingerprint contradictions, and returns normalized `duplicate-v2` score breakdowns.
5. **University Matching API (`POST /api/v1/matching/{problem_id}`)**:
   - **Endpoint Verified**: Endpoint successfully parses input, executes categorization adapter validation, checks matching applicability gates, computes 7-factor weighted scores, and formats responses.
   - **DB Dependency Notice**: Matching requires active, pre-seeded university records (`status: ACTIVE`) in the `universities` collection to generate non-empty candidate matches.

---

## End-to-End Workflow Implementation Status

```
[Implemented] Problem Submission Intake
     │
[Implemented] AI Classification Engine (Gemma 3 4B)
     │
[Implemented] Duplicate Detection Engine (BGE-small + Haversine)
     │
[Implemented] Human-in-the-Loop Reviewer Actions (Backend/QA Console)
     │
[Implemented] Government / Research Routing Gates
     │
[Implemented] 7-Factor University Matching Engine
     │
[Implemented] Sequential Assignment Workflow State Machine
     │
[Implemented] Industry Marketplace & Collaboration Interest Flow
     │
[Pending Integration] Project Lifecycle & Milestone Verification UI
     │
[Pending Integration] Automated Public Notification Dispatch
```

---

## Human-in-the-Loop Decision Boundaries

CivicFix strictly separates **AI assistance** from **consequential decisions**:

- **AI Responsibilities**:
  - Classify text into primary/secondary taxonomy domains.
  - Assess severity, urgency, and routing applicability flags.
  - Calculate embedding similarity and geographic proximity.
  - Compute capability match scores for universities.
  - Flag low-confidence outputs or potential duplicate candidates.

- **Human Reviewer / Officer Responsibilities**:
  - **Review Queue Intervention**: Review cases where `confidence < 0.85` or ambiguity is detected.
  - **Category Correction (`CORRECT`)**: Override incorrect AI classifications (creates a new reviewer version snapshot while preserving historical AI interpretations).
  - **Duplicate Merge (`MERGE_DUPLICATE`)**: Link duplicate submissions to a master problem (preserves original submitter records intact).
  - **Assignment Accept/Reject**: University SPOCs accept or reject project assignments with documented reasons.
  - **Collaboration Approval**: Project owners accept or reject industry partner interest.

---

## Role-Based Architecture (SRS Alignment)

The CivicFix Software Requirements Specification (SRS) defines 12 distinct platform roles:

| Role Category | Roles Defined in SRS | Current Status |
|---|---|---|
| **Public & Citizens** | Citizen, Community / Institutional Submitter | Submissions backend & QA form implemented |
| **Review & Moderation** | Reviewer / Moderator | Action endpoints, queue logic & QA controls implemented |
| **Government** | Government Officer, Government Department Admin | Routing logic implemented; role portal UI pending |
| **Academia** | University SPOC, Faculty Mentor, Student | Scorer, assignment workflow & CRUD implemented |
| **Industry & Partners**| Industry / Startup / MSME Partner, CSR Organization | Marketplace & collaboration flow implemented |
| **Administration** | Platform Administrator, System Administrator | Database index & configuration management implemented |

---

## Security & Protection

- **Credentials Safeguard**: `.env` is explicitly ignored in `.gitignore`. Secrets, database passwords, and JWT signing keys are never checked into Git.
- **Input Sanitization**: All text inputs undergo HTML/script stripping via [`app/core/preprocessor.py`](file:///d:/CivicFix/civicfix-engine/app/core/preprocessor.py).
- **Taxonomy Validation**: Strict Pydantic and custom validator checks prevent injection of invalid domain strings.
- **Auditability**: All state transitions and human reviewer actions log append-only events to the audit trail.

---

## Common Error Codes

| Error Code | HTTP Status | Meaning / Trigger Condition |
|---|---|---|
| `INVALID_INPUT` | `422` | Request body failed Pydantic schema validation |
| `INVALID_TAXONOMY_CATEGORY` | `422` | AI or client provided a primary domain/subcategory outside the controlled taxonomy |
| `AI_INVALID_JSON` | `200 / 500` | LLM response could not be parsed as valid JSON |
| `AI_VALIDATION_ERROR` | `200 / 500` | LLM response failed schema validation |
| `AI_PROVIDER_TIMEOUT` | `500` | Ollama server took longer than `LLM_TIMEOUT_SECONDS` (60s) |
| `AI_PROVIDER_UNAVAILABLE` | `500` | Ollama server is offline or unreachable on port 11434 |
| `INTERNAL_SERVER_ERROR` | `500` | Unhandled internal exception caught by FastAPI handler |

---

## System Status Summary

| Component / Module | Implementation Status | Test Coverage |
|---|---|---|
| **AI Classification Engine** | Integrated in `civicfix-engine` | Unit & schema tests passing |
| **Duplicate Detection Engine** | Integrated in `civicfix-engine` | Unit & math tests passing |
| **University Matching Engine** | Integrated in `civicfix-engine` | 7-factor unit tests passing |
| **Sequential Assignment Workflow**| Integrated in `civicfix-engine` | State machine tests passing |
| **Industry Marketplace** | Integrated in `civicfix-engine` | Filter & search tests passing |
| **Unified Database (`civicfix`)** | Integrated with auto-indexing | Mongomock integration tests passing |
| **Internal Python Service Wiring** | Complete (Zero HTTP overhead) | End-to-end pipeline tests passing |
| **Developer QA Testing Console** | Implemented (`testing-console`) | 14 interactive views functional |
| **Role-Based Production Frontend**| Planned for future release | UI integration pending |

---

## Troubleshooting Guide

### 1. MongoDB Connection Failure
- **Symptom**: `ServerSelectionTimeoutError` or database warning during startup.
- **Fix**: Ensure MongoDB is running locally (`net start MongoDB` or `mongod`). If using MongoDB Atlas, check that your IP address is whitelisted in Atlas Network Access settings and verify `MONGO_URI` in `.env`.

### 2. Ollama / Gemma Model Missing
- **Symptom**: `AI_PROVIDER_UNAVAILABLE` or model error on `/classify`.
- **Fix**: Ensure Ollama is running (`ollama serve`) and verify `gemma3:4b` is installed by running:
  ```powershell
  ollama list
  ollama pull gemma3:4b
  ```

### 3. Port 8000 Already in Use
- **Symptom**: `[Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)`.
- **Fix**: Identify and stop the process occupying port 8000, or start Uvicorn on an alternative port:
  ```powershell
  uvicorn app.main:app --reload --port 8005
  ```

### 4. University Matching Returns Zero Candidates
- **Symptom**: `topUniversities` array is empty when calling `POST /api/v1/matching/{problem_id}`.
- **Fix**: Ensure the database contains active university profiles. Seed sample universities using the `POST /api/v1/universities` endpoint or run database seed scripts.

---

## Development & Contributing

1. **Create Feature Branch**: Always create a feature branch off `main` (e.g., `feature/your-feature-name`).
2. **Commit Guidelines**: Follow conventional commit formats (e.g. `feat(engine): ...`, `fix(matching): ...`).
3. **Run Verification**: Ensure all tests pass (`python -m pytest tests -v`) before opening a Pull Request.

---

## License

This project is open-source under the [MIT License](LICENSE).
