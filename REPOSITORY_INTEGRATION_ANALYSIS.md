# CivicFix — Complete Repository Integration Analysis & Merge Blueprint

> **DOCUMENT STATUS**: [CURRENT] [VERIFIED] Source of truth for repository architecture and future feature merge blueprint.  
> **AUDIT MANDATE**: Reflects the executable code and documentation currently present in the repository. Contains NO hypothetical assumptions or premature refactoring.  
> **EXECUTION CONSTRAINT**: NO implementation code was modified during this phase.

---

## 1. Executive Summary

This document presents a comprehensive technical audit of the **CivicFix** repository. The audit evaluates the three core independent feature modules currently in the project and establishes a formal blueprint for integrating them into a unified, modular architecture.

### The Three Core Features Identified:

1. **Feature 1: AI Classification Engine (`classification-engine/`)**  
   Standalone microservice running **FastAPI**, **Pydantic v2**, and **Ollama (Gemma 3 4B)** on **Port 8000**. Evaluates citizen problem text against a 12-domain controlled taxonomy, extracts 9 qualitative severity factors, urgency, required expertise, and resources, and computes an AI confidence estimate.

2. **Feature 2: Duplicate Candidate Detection Engine (`duplicate-detection/`)**  
   Standalone microservice running **FastAPI**, **Sentence-Transformers (BAAI/bge-small-en-v1.5)**, and **scikit-learn** on **Port 8001**. Encodes problem titles and descriptions into 384-dimensional dense vectors, calculates cosine similarity and Haversine distance, applies Available-Signal Normalized Scoring (v2), and ranks candidate duplicates for human reviewer inspection.

3. **Feature 3: University & R&D Capability Matching Engine (`UniversityMatchingAlgo/`)**  
   Standalone module running **FastAPI** and **PyMongo** on **Port 8003** (or integrated via `UniversityMatchingAlgo/backend/`). Computes 7-factor weighted capability scores (expertise, faculty, capacity, past projects, infrastructure, industry ecosystem, geography), ranks top-5 candidate universities, manages sequential assignment workflows, and supports industry marketplace/collaboration flows.

### Supporting Platform Services:
- **Main Backend Orchestrator (`backend/`)**: FastAPI service on **Port 8002** managing canonical problem state transitions (`SUBMITTED` $\rightarrow$ `CLASSIFIED` $\rightarrow$ `IN_REVIEW` $\rightarrow$ `ROUTED`), audit logs, and reviewer actions.
- **Testing Console (`testing-console/`)**: React 19 + TypeScript + Vite QA console on **Port 5173** providing 14 interactive testing and monitoring views.

---

## 2. Repository Structure

```text
CivicFix/
├── classification-engine/         # Feature 1: Standalone AI Classification Service (:8000)
│   ├── app/
│   │   ├── ai/                    # Ollama provider, prompt generator & LLM interface
│   │   ├── schemas/               # Input/Output Pydantic contracts
│   │   ├── services/              # Preprocessor, classifier & confidence engine
│   │   ├── taxonomy/              # 12-domain controlled taxonomy dictionary
│   │   ├── config.py              # Settings (BaseSettings)
│   │   └── main.py                # FastAPI entry point
│   ├── tests/                     # 70 automated tests
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md
│
├── duplicate-detection/           # Feature 2: Standalone Duplicate Candidate Detection Service (:8001)
│   ├── app/
│   │   ├── schemas/               # Input/Output Pydantic contracts
│   │   ├── services/              # Embedding service (bge-small), location, similarity, detector
│   │   ├── config.py              # Multi-factor weights & thresholds
│   │   └── main.py                # FastAPI entry point
│   ├── experiments/               # Benchmark similarity experiments
│   ├── tests/                     # 38 automated tests
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md
│
├── UniversityMatchingAlgo/        # Feature 3: University & R&D Capability Matching Engine (:8003)
│   ├── backend/
│   │   ├── app/
│   │   │   ├── config/            # Database connection & Pydantic settings
│   │   │   ├── core/              # Dev auth & normalizers
│   │   │   ├── integrations/      # Categorization adapter (upstream black box translation)
│   │   │   ├── models/            # Persisted PyMongo/Pydantic models
│   │   │   ├── routers/           # REST endpoints (matching, assignments, marketplace, etc.)
│   │   │   ├── schemas/           # Request/Response DTOs
│   │   │   ├── services/          # 7-factor scoring engine, ranking, assignment, marketplace
│   │   │   └── tests/             # Automated test suite
│   │   ├── seed/                  # Seed datasets (universities, solutions, partners, problems)
│   │   ├── .env.example
│   │   ├── requirements.txt
│   │   └── README.md
│   ├── frontend-test/             # Demo HTML/JS test client
│   ├── IMPLEMENTATION_PLAN.md
│   └── README.md
│
├── backend/                       # Platform Host: Main Backend Orchestrator (:8002)
│   ├── app/
│   │   ├── api/                   # Problems, reviewer, routing, health endpoints
│   │   ├── clients/               # HTTP client wrappers for :8000 and :8001
│   │   ├── models/                # Problem, version, review, audit, duplicate models
│   │   ├── repositories/          # MongoDB / Memory fallback repositories
│   │   ├── services/              # Orchestrator, reviewer, routing, audit services
│   │   ├── config.py              # Backend service URLs & settings
│   │   └── main.py                # FastAPI entry point
│   ├── requirements.txt
│   └── README.md
│
├── testing-console/               # Platform Host: React/Vite QA Console (:5173)
│   ├── src/
│   │   ├── api/                   # API clients for :8000, :8001, :8002, :11434
│   │   ├── components/            # Reusable UI widgets (JsonViewer, StatusBadge)
│   │   ├── views/                 # 14 QA test views
│   │   ├── config.ts              # Config & localStorage overrides
│   │   ├── types.ts               # Shared TypeScript types
│   │   └── App.tsx                # Main router & layout
│   ├── package.json
│   ├── vite.config.ts
│   └── README.md
│
├── integration-tests/             # End-to-end integration test suite
├── AI_LOGIC_README.md             # Comprehensive AI execution logic documentation
├── INTEGRATION_GUIDE.md           # Cross-repository integration guide
└── REPOSITORY_INTEGRATION_ANALYSIS.md # This document
```

---

## 3. Identified Three Features Overview

| Feature Attribute | Feature 1: Classification Engine | Feature 2: Duplicate Detection Engine | Feature 3: University Matching Engine |
|---|---|---|---|
| **Component Name** | Classification Engine | Duplicate Detection Engine | University & R&D Capability Matching Engine |
| **Folder Location** | `classification-engine/` | `duplicate-detection/` | `UniversityMatchingAlgo/` |
| **Backend Framework**| FastAPI (Python 3.11+) | FastAPI (Python 3.11+) | FastAPI (Python 3.11+) |
| **Primary Entry Point**| `app/main.py` | `app/main.py` | `backend/app/main.py` |
| **Default Port** | `8000` | `8001` | `8003` (or `8000` in isolated setup) |
| **Core AI / ML Model** | Gemma 3 4B (`gemma3:4b` via Ollama) | BAAI/bge-small-en-v1.5 (SentenceTransformers) | Multi-Criteria Scoring & Ranking Engine (7-Factor) |
| **Main API Endpoint** | `POST /classify` | `POST /duplicate-check` | `POST /api/matching/run` |
| **Persistence Model** | Stateless (In-Memory processing) | Stateless (In-Memory candidate processing) | PyMongo (MongoDB collections: `universities`, `solutions`, etc.) |
| **Primary Output** | Taxonomy, severity factors, urgency, confidence | Ranked duplicate candidates, scores, explainable reasons | Ranked Top-5 universities, score breakdown, assignment chain |

---

## 4. Feature 1 Analysis — AI Classification Engine

### Purpose
Processes citizen-reported problem text to generate structured AI classifications, assign 12-domain taxonomy categories, evaluate 9 qualitative severity factors, rate urgency, and compute an AI confidence score.

### Responsibilities
- Text preprocessing & whitespace sanitization.
- Gemma 3 4B prompt construction with embedded 12-domain taxonomy.
- Parsing structured JSON via Pydantic (`ClassificationResult`).
- Business & taxonomy rule validation (`app/taxonomy/taxonomy.py`).
- Evidence sufficiency evaluation & vague submission flagging.
- Secondary domain classification (enforcing distinct evidence rules).
- Confidence threshold evaluation (`confidence >= 0.85` $\rightarrow$ `classified`, else `review_required`).

### APIs
- **`GET /health`**: Health check probe returning `{"status": "healthy"}`.
- **`POST /classify`**:
  - *Input (`ProblemClassificationInput`)*: `problemId`, `title`, `description`, `location` (`district`, `state`, `latitude`, `longitude`).
  - *Output (`ClassificationResponse`)*: `problemId`, `status` (`classified` | `review_required` | `failed`), `classification` (`primaryDomain`, `subcategory`, `secondaryDomains`, `severity`, `severityAssessment`, `severityEvidence`, `peopleAffected`, `urgency`, `researchRequired`, `governmentActionPossible`, `requiredExpertise`, `requiredResources`, `confidence`, `reasoning`), `error`.

### Services & Schemas
- **Services**: `ClassifierService` (`app/services/classifier.py`), `sanitize_and_preprocess` (`app/services/preprocessor.py`), `evaluate_confidence` (`app/services/confidence.py`), `OllamaProvider` (`app/ai/ollama.py`).
- **Schemas**: `ProblemClassificationInput`, `ClassificationResult`, `SeverityAssessment`, `PeopleAffected`, `ClassificationResponse`, `StatusEnum`.

### Configuration & Environment
- `OLLAMA_BASE_URL` (`http://localhost:11434`)
- `OLLAMA_MODEL` (`gemma3:4b`)
- `LLM_TIMEOUT_SECONDS` (`60.0`)
- `LLM_MAX_RETRIES` (`3`)
- `AI_HIGH_CONFIDENCE_THRESHOLD` (`0.85`)
- `AI_REVIEW_THRESHOLD` (`0.60`)

### Tests & Verified Results
- **Test Directory**: `classification-engine/tests/`
- **Coverage**: 70 tests covering API routes, taxonomy validation, severity framework, confidence thresholds, Ollama provider retries, prompt injection security, and regression cases 1–5.
- **Verified Status**: **70 Passed, 0 Failed**.

---

## 5. Feature 2 Analysis — Duplicate Candidate Detection Engine

### Purpose
Calculates semantic vector similarity, taxonomy signal overlap, and physical geographic distance to identify and rank candidate duplicate problem reports for human reviewer decision.

### Responsibilities
- Generating 384-dimensional dense vector embeddings using `BAAI/bge-small-en-v1.5`.
- Computing cosine similarity between normalized embeddings.
- Haversine distance calculation and location proximity decay scoring.
- Evaluating taxonomy signal matches (`primaryDomain`, `subcategory`, `secondaryDomains`).
- Available-Signal Normalized Scoring (v2) dynamically excluding missing metadata.
- Ranking candidates and generating explainable human-readable reasons.

### APIs
- **`GET /health`**: Returns status, embedding model metadata, and thresholds.
- **`POST /duplicate-check`**:
  - *Input (`DuplicateCheckRequest`)*: `problem` (`ProblemInput`), `candidates` (`List[ProblemInput]`), `topK` (`int`).
  - *Output (`DuplicateCheckResponse`)*: `problemId`, `status` (`candidate_found` | `no_candidate`), `duplicateCandidates` (`List[CandidateMatch]` containing `candidateProblemId`, `duplicateScore`, `semanticSimilarity`, `primaryDomainMatch`, `subcategoryMatch`, `secondaryDomainOverlap`, `locationDistanceKm`, `locationScore`, `candidateStatus`, `scoreBreakdown`, `reasons`), `scoringVersion`.

### Services & Schemas
- **Services**: `DuplicateDetector` (`app/services/duplicate_detector.py`), `EmbeddingService` (`app/services/embedding.py`), `CandidateRetriever` (`app/services/candidate_retriever.py`), `LocationService` (`app/services/location.py`), `SimilarityService` (`app/services/similarity.py`).
- **Schemas**: `DuplicateCheckRequest`, `ProblemInput`, `LocationInput`, `DuplicateCheckResponse`, `CandidateMatch`.

### Configuration & Environment
- `EMBEDDING_MODEL` (`BAAI/bge-small-en-v1.5`)
- `EMBEDDING_DIMENSION` (`384`)
- `VECTOR_TOP_K` (`10`)
- `DUPLICATE_SIMILARITY_THRESHOLD` (`0.75`)
- `LOCATION_DISTANCE_THRESHOLD_KM` (`5.0`)
- `SEMANTIC_WEIGHT` (`0.50`), `PRIMARY_DOMAIN_WEIGHT` (`0.15`), `SUBCATEGORY_WEIGHT` (`0.15`), `SECONDARY_DOMAIN_WEIGHT` (`0.10`), `LOCATION_WEIGHT` (`0.10`).

### Tests & Verified Results
- **Test Directory**: `duplicate-detection/tests/`
- **Coverage**: 38 tests covering embeddings, similarity math, candidate retrieval, location decay, missing metadata, hospital regression scenarios, and 52-case evaluation benchmark.
- **Verified Status**: **38 Passed, 0 Failed**.

---

## 6. Feature 3 Analysis — University & R&D Capability Matching Engine

### Purpose
Matches structured social-impact problems against higher education institution (HEI) research capabilities, ranks top-5 best-fit universities using a 7-factor weighted scoring algorithm, manages sequential assignment workflows, and powers an industry marketplace for solution co-creation.

### Responsibilities
- Upstream classification JSON adaptation (`app/integrations/categorization_adapter.py`).
- 7-Factor Weighted Scoring (`expertise`, `faculty`, `capacity`, `past_projects`, `infrastructure`, `industry_ecosystem`, `geography`).
- Ranking top-5 universities with deterministic tie-breaking logic.
- Managing university assignment state transitions (`PENDING` $\rightarrow$ `SENT` $\rightarrow$ `ACCEPTED` / `REJECTED` / `EXPIRED`).
- Supporting industry marketplace solution listings, interest expressions, and collaboration creation.
- MongoDB persistence for universities, assignments, solutions, and collaborations.

### APIs
- **`GET /api/health`**: Health probe returning `{"status": "ok"}`.
- **`POST /api/matching/run`**: Evaluates problem input against university database and returns ranked matches.
- **`POST /api/matching/run-raw`**: Accepts raw Classification Engine JSON output via `categorization_adapter` and executes matching.
- **`POST /api/assignments/create`**: Initializes sequential assignment chain.
- **`POST /api/assignments/{assignment_id}/respond`**: Accepts/rejects university assignment.
- **`GET /api/marketplace/solutions`**: Lists marketplace solutions with filtering.
- **`POST /api/interests/express`**: Submits industry partner interest.
- **`POST /api/collaborations/create`**: Creates active collaboration project.

### Services & Schemas
- **Services**: `MatchingEngine` (`app/services/matching_engine.py`), `RankingService` (`app/services/ranking.py`), `AssignmentWorkflowService` (`app/services/assignment_workflow.py`), `MarketplaceService` (`app/services/marketplace.py`), `CollaborationService` (`app/services/collaboration.py`), 7 scoring factor services (`app/services/scoring/`).
- **Schemas**: `ProblemInput`, `MatchRequest`, `MatchResponse`, `UniversityScoreBreakdown`, `AssignmentResponse`, `SolutionResponse`, `CollaborationResponse`.

### Configuration & Environment
- `MONGO_URI` (`mongodb://localhost:27017`)
- `MONGO_DB_NAME` (`university_matching`)
- `DEFAULT_ASSIGNMENT_DEADLINE_HOURS` (`48`)
- `DEFAULT_REMINDER_WINDOW_HOURS` (`12`)
- `DEV_MODE` (`True`)

### Tests & Verified Results
- **Test Directory**: `UniversityMatchingAlgo/backend/app/tests/`
- **Coverage**: Pytest suite covering all 7 scoring factors, ranking, tie-breakers, assignment state machine transitions, marketplace filtering, and collaboration creation.

---

## 7. Current System Architecture

```text
[Citizen / QA User] ──► Testing Console (React/Vite @ Port 5173)
                             │
                             ├───────────────────────────────┬──────────────────────────────┐
                             ▼ (HTTP REST)                   ▼ (HTTP REST)                  ▼ (HTTP REST)
                 Classification Engine           Duplicate Detection Engine      Main Backend Orchestrator
                    (Port 8000)                     (Port 8001)                     (Port 8002)
                         │                               │                               │
                         ▼                               ▼                               ▼
                   Ollama Local                 Sentence-Transformers              MongoDB / Memory
                   (Gemma 3 4B)                (bge-small-en-v1.5)               (Database: civicfix)
                         :                               :
                         :...............................:
                                         │
                                         ▼ (Current Manual / Adapter Gap)
                             University Matching Engine
                                    (Port 8003)
                                         │
                                         ▼
                                  MongoDB Atlas / Local
                                (Database: university_matching)
```

### Architectural State Observations:
- **Feature 1 and Feature 2** operate as stateless, independent FastAPI microservices over REST.
- **Main Backend Orchestrator** calls Feature 1 (`classification_client.py`) and Feature 2 (`duplicate_client.py`) via HTTP async REST calls.
- **Feature 3 (`UniversityMatchingAlgo`)** currently runs as a standalone FastAPI backend with PyMongo, consuming upstream classification outputs via an integration adapter (`app/integrations/categorization_adapter.py`).

---

## 8. API Inventory

| Feature | Method | Path | Purpose | Database Interaction | Current Status |
|---|---|---|---|---|---|
| **Feature 1** | `GET` | `/health` | Service health check | None | [CURRENT] Implemented |
| **Feature 1** | `POST` | `/classify` | Classify citizen report | None (Stateless) | [CURRENT] Implemented |
| **Feature 2** | `GET` | `/health` | Service & model health | None | [CURRENT] Implemented |
| **Feature 2** | `POST` | `/duplicate-check` | Surface duplicate candidates | None (Stateless) | [CURRENT] Implemented |
| **Feature 3** | `GET` | `/api/health` | Service health check | PyMongo ping | [CURRENT] Implemented |
| **Feature 3** | `POST` | `/api/matching/run` | Run university matching | Reads `universities` | [CURRENT] Implemented |
| **Feature 3** | `POST` | `/api/matching/run-raw`| Run adapter + matching | Reads `universities`, writes `matching_results` | [CURRENT] Implemented |
| **Feature 3** | `POST` | `/api/assignments/create` | Create assignment chain | Writes `university_assignments` | [CURRENT] Implemented |
| **Feature 3** | `POST` | `/api/assignments/{id}/respond` | SPOC accept/reject | Updates `university_assignments` | [CURRENT] Implemented |
| **Feature 3** | `GET` | `/api/marketplace/solutions` | Search solutions | Reads `solutions` | [CURRENT] Implemented |
| **Feature 3** | `POST` | `/api/interests/express` | Submit partner interest | Writes `industry_interests` | [CURRENT] Implemented |
| **Feature 3** | `POST` | `/api/collaborations/create` | Create collaboration | Writes `collaborations` | [CURRENT] Implemented |
| **Backend** | `POST` | `/api/problems` | Submit citizen problem | Writes `problems`, calls :8000 & :8001 | [CURRENT] Implemented |
| **Backend** | `GET` | `/api/reviewer/queue` | List flagged queue | Reads `problems` | [CURRENT] Implemented |
| **Backend** | `POST` | `/api/reviewer/action` | Execute reviewer action | Updates `problems`, `problem_versions` | [CURRENT] Implemented |

---

## 9. MongoDB Architecture & Collections

Currently, database storage is split across two separate database names:

1. **Main Backend DB (`civicfix`)**:
   - `problems`: Canonical operational problem records.
   - `problem_versions`: Audit trail snapshots of problem edits.
   - `ai_analysis`: Stored classification results.
   - `duplicate_candidates`: Stored candidate links and scores.
   - `reviews`: Log of reviewer decisions.
   - `audit`: Append-only audit trail events.

2. **University Matching DB (`university_matching`)**:
   - `universities`: University profiles, faculties, research capacity, and infrastructure.
   - `solutions`: R&D solutions listed on the industry marketplace.
   - `university_assignments`: Sequential assignment workflow records.
   - `industry_interests`: Industry partner expressions of interest.
   - `matching_results`: Stored university matching results.
   - `matching_configuration`: Weight configurations for matching runs.
   - `collaborations`: Active project collaboration documents.

### MongoDB Collections Summary Table

| Collection Name | Used By Module | Primary Key / Index | Main Fields | Read/Write | Current Status |
|---|---|---|---|---|---|
| `problems` | Main Backend | `problemId` (unique) | `problemId`, `title`, `description`, `location`, `status`, `primaryDomain`, `secondaryDomains`, `severity`, `confidence` | Read / Write | [CURRENT] Implemented |
| `problem_versions` | Main Backend | `versionId` (unique), `problemId` | `versionId`, `problemId`, `versionNumber`, `snapshot`, `createdBy` | Read / Write | [CURRENT] Implemented |
| `ai_analysis` | Main Backend | `analysisId` (unique), `problemId` | `analysisId`, `problemId`, `classification`, `rawResponse` | Write | [CURRENT] Implemented |
| `duplicate_candidates` | Main Backend | `candidateId` (unique), `problemId` | `candidateId`, `problemId`, `targetProblemId`, `score`, `reasons` | Write | [CURRENT] Implemented |
| `reviews` | Main Backend | `reviewId` (unique), `problemId` | `reviewId`, `problemId`, `action`, `reviewerNotes`, `timestamp` | Write | [CURRENT] Implemented |
| `audit` | Main Backend | `eventId` (unique), `problemId` | `eventId`, `problemId`, `actionType`, `actor`, `details` | Write | [CURRENT] Implemented |
| `universities` | Feature 3 | `universityId` (unique), `expertise`, `status` | `universityId`, `name`, `expertise`, `departments`, `facilities`, `location` | Read / Write | [CURRENT] Implemented |
| `solutions` | Feature 3 | `solutionId` (unique), `domain`, `status` | `solutionId`, `universityId`, `title`, `description`, `domain`, `status` | Read / Write | [CURRENT] Implemented |
| `university_assignments`| Feature 3 | `assignmentId` (unique), `problemId` | `assignmentId`, `problemId`, `universityId`, `status`, `deadline` | Read / Write | [CURRENT] Implemented |
| `industry_interests` | Feature 3 | `interestId` (unique), `solutionId` | `interestId`, `partnerId`, `solutionId`, `status`, `notes` | Read / Write | [CURRENT] Implemented |
| `matching_results` | Feature 3 | `problemId` | `problemId`, `rankedUniversities`, `timestamp` | Write | [CURRENT] Implemented |
| `collaborations` | Feature 3 | `collaborationId` (unique) | `collaborationId`, `problemId`, `solutionId`, `universityId`, `status` | Write | [CURRENT] Implemented |

---

## 10. Data Ownership Matrix

| Data Entity / Collection | Primary Owning Feature / Module | Reader Modules | Writer Modules |
|---|---|---|---|
| `problems` | Main Backend Orchestrator | Feature 1, Feature 2, Feature 3 | Main Backend Orchestrator |
| `ai_analysis` | Feature 1 (Classification) | Main Backend, Feature 3 Adapter | Main Backend Orchestrator |
| `duplicate_candidates` | Feature 2 (Duplicate Detection) | Main Backend, Reviewer Queue | Main Backend Orchestrator |
| `universities` | Feature 3 (University Matching) | Feature 3 Matching Engine | Feature 3 Admin / Seed |
| `university_assignments` | Feature 3 (University Matching) | Feature 3 Workflow, Reviewer | Feature 3 Workflow Service |
| `solutions` | Feature 3 (Marketplace) | Feature 3 Marketplace, Industry | Feature 3 Marketplace Service |
| `collaborations` | Feature 3 (Collaboration) | Feature 3, Industry, HEI | Feature 3 Collaboration Service |
| `audit` | Main Backend Orchestrator | Security / Audit Viewer | Main Backend Orchestrator |

---

## 11. Shared Data Model Analysis

The following primary fields are shared across the three features:

| Field Name | Type | Producer | Consumers | Source of Truth | Conflict / Alignment Note |
|---|---|---|---|---|---|
| `problemId` | `str` | Main Backend | Feature 1, Feature 2, Feature 3 | `problems.problemId` | Uniform string identifier across all 3 modules. |
| `title` | `str` | Citizen Submission | Feature 1, Feature 2 | `problems.title` | Trimmed string, max 300 chars. |
| `description` | `str` | Citizen Submission | Feature 1, Feature 2 | `problems.description` | Trimmed string, max 5000 chars. |
| `location` | `Object` | Citizen Submission | Feature 1, Feature 2, Feature 3 | `problems.location` | Feature 1/2 use `lat`/`long`/`district`/`state`. Feature 3 uses `district`/`state`. |
| `primaryDomain` | `str` | Feature 1 (AI) | Feature 2, Feature 3 | `ai_analysis.primaryDomain` | String matching 1 of 12 controlled taxonomy keys. |
| `subcategory` | `str` | Feature 1 (AI) | Feature 2, Feature 3 | `ai_analysis.subcategory` | String matching valid subcategory for `primaryDomain`. |
| `secondaryDomains` | `List[str]`| Feature 1 (AI) | Feature 2, Feature 3 | `ai_analysis.secondaryDomains` | List of valid primary domain keys. |
| `requiredExpertise` | `List[str]`| Feature 1 (AI) | Feature 3 | `ai_analysis.requiredExpertise` | Key input for Feature 3 scoring. |
| `requiredResources` | `List[str]`| Feature 1 (AI) | Feature 3 | `ai_analysis.requiredResources` | Key input for Feature 3 scoring. |
| `researchRequired` | `bool` | Feature 1 (AI) | Feature 3 | `ai_analysis.researchRequired` | Gate condition for Feature 3 matching. |

---

## 12. ID & Reference Analysis

1. **Problem Identifier (`problemId`)**:
   - Format: String (e.g. `"P1001"`, `"PROB-99214"`).
   - Uniformly used as foreign reference in `ai_analysis`, `duplicate_candidates`, `university_assignments`, and `matching_results`.

2. **MongoDB `_id`**:
   - `BSON ObjectId` generated automatically by PyMongo / Motor.
   - When models expose JSON APIs, `_id` is excluded (`doc.pop("_id", None)`) in favor of string business IDs (`problemId`, `universityId`, `assignmentId`).

3. **University Identifier (`universityId`)**:
   - Format: String (e.g. `"UNI-101"`, `"IIT-BOM-01"`).

4. **Assignment Identifier (`assignmentId`)**:
   - Format: String (e.g. `"ASGN-88021"`).

---

## 13. Status & Enum Alignment Matrix

| Status Domain | Field Name | Feature | Allowed Enum Values | Conflict / Alignment Note |
|---|---|---|---|---|
| **Classification** | `status` | Feature 1 | `"classified"`, `"review_required"`, `"failed"` | Standardized snake_case lower strings. |
| **Duplicate Result** | `status` | Feature 2 | `"candidate_found"`, `"no_candidate"` | Standardized snake_case lower strings. |
| **Candidate Match** | `candidateStatus` | Feature 2 | `"strong_candidate"`, `"potential_duplicate"`, `"no_candidate"` | Standardized snake_case lower strings. |
| **Main Workflow** | `status` | Backend | `"SUBMITTED"`, `"CLASSIFIED"`, `"IN_REVIEW"`, `"ROUTED"`, `"ASSIGNED"`, `"RESOLVED"`, `"REJECTED"` | Upper-case status strings. |
| **Assignment State** | `status` | Feature 3 | `"PENDING"`, `"SENT"`, `"ACCEPTED"`, `"REJECTED"`, `"EXPIRED"` | Upper-case status strings. |
| **Solution Visibility**| `visibility` | Feature 3 | `"PUBLIC"`, `"PRIVATE"`, `"PARTNER_ONLY"` | Upper-case enum values. |

---

## 14. AI & ML Component Analysis

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ Feature 1: Classification Engine                                        │
│  - Model: Gemma 3 4B (gemma3:4b) via local Ollama API                    │
│  - Context Length: 131,072 tokens | Temp: 0.1                            │
│  - Format: Constrained Pydantic JSON Schema                             │
│  - Timeouts: 60.0s timeout, 3 exponential backoff retries               │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ Feature 2: Duplicate Detection Engine                                   │
│  - Model: BAAI/bge-small-en-v1.5 (SentenceTransformers)                │
│  - Dense Vector: 384 dimensions (L2 normalized)                         │
│  - Similarity: Cosine similarity + Haversine distance decay (5km radius) │
│  - Scoring: Available-Signal Normalized Scoring (v2)                    │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ Feature 3: University Capability Matching Engine                        │
│  - Algorithm: 7-Factor Weighted Scoring Engine                           │
│  - Scoring Weights: Expertise (0.30), Faculty (0.15), Capacity (0.15),    │
│    Past Projects (0.15), Infrastructure (0.10), Ecosystem (0.10),        │
│    Geography (0.05)                                                     │
│  - Ranking: Top-5 candidate ranking with tie-breaker logic               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 15. Dependencies & Environment Configuration

### Combined Dependencies (Python):
- `fastapi >= 0.110.0`
- `uvicorn[standard] >= 0.28.0`
- `pydantic >= 2.6.0`
- `pydantic-settings >= 2.2.0`
- `python-dotenv >= 1.0.1`
- `sentence-transformers >= 2.5.0`
- `scikit-learn >= 1.4.0`
- `numpy >= 1.26.0`
- `pymongo >= 4.6.0`
- `httpx >= 0.27.0`
- `pytest >= 8.0.0`
- `pytest-asyncio >= 0.23.0`

### Combined Environment Variables (`.env.example`):
```env
# Server & Database Configuration
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=civicfix

# Feature 1 - AI Classification Engine Settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
LLM_TIMEOUT_SECONDS=60.0
LLM_MAX_RETRIES=3
AI_HIGH_CONFIDENCE_THRESHOLD=0.85
AI_REVIEW_THRESHOLD=0.60

# Feature 2 - Duplicate Detection Settings
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DIMENSION=384
VECTOR_TOP_K=10
DUPLICATE_SIMILARITY_THRESHOLD=0.75
LOCATION_DISTANCE_THRESHOLD_KM=5.0

# Feature 3 - University Matching Settings
DEFAULT_ASSIGNMENT_DEADLINE_HOURS=48
DEFAULT_REMINDER_WINDOW_HOURS=12
DEV_MODE=True
```

---

## 16. Integration Risk Analysis

| Risk ID | Feature(s) Affected | Evidence / Cause | Severity | Proposed Future Resolution |
|---|---|---|---|---|
| **R-01** | Feature 3 $\leftrightarrow$ Backend | Database split (`civicfix` vs `university_matching`) | **High** | Consolidate all collections into single MongoDB database (`civicfix`). |
| **R-02** | Feature 3 $\leftrightarrow$ Feature 1 | Schema translation adapter (`categorization_adapter.py`) | **Medium** | Direct internal service invocation using shared Pydantic DTOs. |
| **R-03** | Feature 1 / 2 / 3 | Multiple standalone FastAPI apps on separate ports (8000, 8001, 8003) | **Medium** | Combine routers into single FastAPI application under `/api/v1`. |
| **R-04** | Feature 2 | Heavy ML model loading (`bge-small-en-v1.5`) per process | **Low** | Pre-load embedding model during FastAPI lifespan startup. |
| **R-05** | Backend | Dual database access (`pymongo` sync vs `motor` async) | **Medium** | Standardize on `motor` async driver across all repositories. |

---

## 17. Components Safe to Merge Directly vs. Requiring Adaptation

### Safe to Merge Directly:
- **Taxonomy Dictionary & Validator** (`classification-engine/app/taxonomy/taxonomy.py`)
- **Embedding Service** (`duplicate-detection/app/services/embedding.py`)
- **Similarity & Location Calculators** (`duplicate-detection/app/services/similarity.py`, `location.py`)
- **7-Factor University Scoring Engine** (`UniversityMatchingAlgo/backend/app/services/scoring/`)
- **Pydantic Data Contracts** (`schemas/`)
- **Pytest Automated Test Suites**

### Components Requiring Adaptation:
- **FastAPI Router Integration**: Combining `main.py` entry points into a single application router structure.
- **Categorization Adapter**: Converting `categorization_adapter.py` from HTTP payload dictionary parsing to direct Pydantic model calls.
- **MongoDB Database Client**: Merging PyMongo and Motor database connection references to point to a single `civicfix` MongoDB instance.

---

## 18. Proposed Combined Module Architecture (PROPOSED - NOT IMPLEMENTED)

```text
PROPOSED COMBINED MODULE ARCHITECTURE
======================================

civicfix-engine/
├── app/
│   ├── main.py                  # Single combined FastAPI entry point
│   ├── config.py                # Unified Pydantic settings & database connection
│   │
│   ├── api/                     # Unified REST API Routers
│   │   ├── v1/
│   │   │   ├── classification.py # POST /api/v1/classify
│   │   │   ├── duplicates.py     # POST /api/v1/duplicate-check
│   │   │   ├── matching.py       # POST /api/v1/matching/run
│   │   │   ├── assignments.py    # POST /api/v1/assignments
│   │   │   └── marketplace.py    # GET  /api/v1/marketplace/solutions
│   │
│   ├── core/                    # Preprocessors, sanitizers, taxonomy
│   │   ├── taxonomy.py
│   │   └── preprocessor.py
│   │
│   ├── schemas/                 # Unified Pydantic DTOs
│   │   ├── classification.py
│   │   ├── duplicate.py
│   │   ├── matching.py
│   │   └── problem.py
│   │
│   ├── services/                # Combined Core Services
│   │   ├── classification_service.py  # (From Feature 1)
│   │   ├── duplicate_service.py       # (From Feature 2)
│   │   ├── matching_service.py        # (From Feature 3)
│   │   ├── embedding_service.py       # (BGE-small 384-d)
│   │   └── scoring/                   # (7-factor university scoring)
│   │
│   └── database/                # Unified MongoDB Motor Async Repositories
│       ├── connection.py
│       ├── problem_repository.py
│       ├── university_repository.py
│       ├── assignment_repository.py
│       └── solution_repository.py
│
├── tests/                       # Integrated Pytest Suite
├── requirements.txt
└── README.md
```

---

## 19. Proposed Unified Data Flow (PROPOSED - NOT IMPLEMENTED)

```text
Citizen Problem Submission (POST /api/v1/problems)
                       │
                       ▼
1. Input Preprocessing & Sanitization
                       │
                       ▼
2. Save Operational Record to MongoDB (`problems` collection, status: "SUBMITTED")
                       │
                       ▼
3. Feature 1: AI Classification Service
   ├── Calls Gemma 3 4B via Ollama
   ├── Evaluates Taxonomy, Severity (9 factors), Urgency & Confidence
   └── Saves result to `ai_analysis` collection
                       │
                       ▼
4. Feature 2: Duplicate Detection Service
   ├── Generates BGE-small 384-d vector embedding
   ├── Scores candidates via Available-Signal Normalization (v2)
   └── Saves candidate links to `duplicate_candidates` collection
                       │
                       ▼
5. Check Decision Boundary:
   ├── IF confidence < 0.85 OR duplicate candidate found:
   │     └─ Route to Human Reviewer Queue (status: "IN_REVIEW")
   └── ELSE:
         └─ Proceed to Automated Routing (status: "CLASSIFIED")
                       │
                       ▼
6. Feature 3: University Capability Matching Service
   ├── Evaluates 7-factor capabilities against problem requirements
   ├── Ranks Top-5 candidate universities
   ├── Saves result to `matching_results` collection
   └── Initializes Sequential Assignment Workflow (`university_assignments`)
                       │
                       ▼
7. Update Canonical Problem Status ("ROUTED" / "ASSIGNED")
```

---

## 20. Future Integration Merge Plan (PROPOSED - NOT IMPLEMENTED)

- **Phase 1: Environment & Repository Preparation**  
  Standardize unified `requirements.txt` and `.env.example`.
- **Phase 2: Database Consolidation**  
  Unify MongoDB database configurations under database `civicfix` with single Motor async connection pool.
- **Phase 3: Schema & DTO Standardization**  
  Consolidate `ProblemInput`, `ClassificationResult`, and `CandidateMatch` Pydantic models into `app/schemas/`.
- **Phase 4: Service Layer Unification**  
  Move `classification_service.py`, `duplicate_service.py`, and `matching_service.py` under `app/services/`.
- **Phase 5: API Router Consolidation**  
  Assemble FastAPI endpoints into `/api/v1/` routes under a single Uvicorn server instance.
- **Phase 6: Integration Testing & Verification**  
  Execute full E2E test suite covering problem intake $\rightarrow$ classification $\rightarrow$ duplicate check $\rightarrow$ university matching $\rightarrow$ assignment workflow.

---

## 21. Open Questions & Unknowns

- **UNKNOWN [U-01]**: Will production deployment host Ollama locally on GPU worker nodes or utilize a centralized AI gateway?
- **UNKNOWN [U-02]**: Will university matching assignments require real-time email/SMS notification dispatches to university SPOCs?
- **UNKNOWN [U-03]**: Should persistent vector search utilize MongoDB Atlas Vector Search indexes or remain in-memory for MVP deployment?

---

## 22. Final Integration Checklist

- [x] Technical audit of all top-level repository directories performed.
- [x] Three core feature modules identified (`classification-engine`, `duplicate-detection`, `UniversityMatchingAlgo`).
- [x] Architecture, APIs, services, schemas, and scoring models documented for each feature.
- [x] MongoDB database collections, indexes, and read/write usage audited.
- [x] Shared data models, IDs, and status enums mapped.
- [x] Integration risks identified and future resolutions proposed.
- [x] Combined module architecture and unified data flow designed.
- [x] `REPOSITORY_INTEGRATION_ANALYSIS.md` created at repository root.
- [x] Zero implementation source code files modified during audit.
