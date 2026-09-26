# CivicFix Duplicate Detection Engine

Standalone semantic duplicate candidate detection microservice. Built with **FastAPI**, **Sentence Transformers**, and **BAAI/bge-small-en-v1.5**.

---

## 1. Purpose

The **CivicFix Duplicate Detection Engine** is an independent AI microservice that identifies, calculates similarity for, ranks, and surfaces candidate duplicate problem reports. When a citizen submits a new problem, the engine compares it against existing master problems in the database to surface potential duplicate candidates with explainable score breakdowns and evidence reasons.

---

## 2. Responsibilities

- **Embedding Generation**: Generating 384-dimensional dense vector embeddings using `BAAI/bge-small-en-v1.5`.
- **Semantic Similarity**: Computing cosine similarity between normalized vector representations.
- **Taxonomy Signal Comparison**: Comparing primary domain, subcategory, and secondary domain overlaps.
- **Location Similarity**: Calculating physical distance using the Haversine formula and location decay scoring.
- **Problem Fingerprint Extraction**: Extracting key entities and issues for contradiction protection.
- **Available-Signal Normalized Scoring (v2)**: Computing multi-factor composite scores dynamically excluding missing metadata from the denominator.
- **Candidate Ranking**: Ordering top candidates by composite duplicate score.
- **Candidate Decision Boundary**: Categorizing candidates into `strong_candidate`, `candidate`, `weak_candidate`, or `no_candidate`.

---

## 3. Important Boundary

> **CRITICAL BOUNDARY:**  
> The Duplicate Detection Engine **DOES NOT**:
> - Automatically merge problem records.
> - Delete, archive, or replace problem reports.
> - Modify the master problem database.
> - Make the final merge decision.
>
> The engine purely surfaces candidate recommendations with transparent, explainable score breakdowns. The consequential merge action belongs strictly to **human reviewers**.

---

## 4. Architecture

```text
Problem Input (New Problem + Candidate Problems)
                      │
                      ▼
1. Input Preprocessing & Embedding Generation (BGE-small-en-v1.5)
                      │
                      ▼
2. Vector Similarity Computation (Cosine Similarity)
                      │
                      ▼
3. Multi-Factor Signal Evaluation:
   ├─ Semantic Weight (0.50)
   ├─ Primary Domain Weight (0.15)
   ├─ Subcategory Weight (0.15)
   ├─ Secondary Domains Weight (0.10)
   └─ Location Proximity Weight (0.10)
                      │
                      ▼
4. Available-Signal Normalized Scoring (v2)
                      │
                      ▼
5. Problem Fingerprint Contradiction Protection
                      │
                      ▼
6. Threshold Evaluation & Candidate Ranking
                      │
                      ▼
 JSON Response (DuplicateCheckResponse with Score Breakdowns & Reasons)
```

---

## 5. v2 Scoring Behavior

The **v2 Available-Signal Normalized Scoring** model handles missing or incomplete metadata gracefully without artificially suppressing candidate scores:

$$\text{NormalizedCompositeScore} = \frac{\sum_{i \in \text{Available}} \text{contribution}_i}{\sum_{i \in \text{Available}} w_i}$$

### Signal State Rules

| Signal | Base Weight ($w_i$) | State Rule & Value |
|---|---|---|
| **Semantic** | `0.50` | Always `AVAILABLE`. Cosine similarity score $[0, 1]$. |
| **Primary Domain** | `0.15` | `MATCH` (1.0), `MISMATCH` (0.0 with weight retained), or `UNKNOWN` (Excluded from denominator when missing). |
| **Subcategory** | `0.15` | `MATCH` (1.0), `MISMATCH` (0.0 with weight retained), or `UNKNOWN` (Excluded from denominator when missing). |
| **Secondary Domains** | `0.10` | Jaccard overlap score $[0, 1]$, or `UNKNOWN` (Excluded from denominator if either missing). |
| **Location** | `0.10` | Haversine distance decay score $\max(0, 1 - d/5.0)$, or `UNAVAILABLE` (Excluded from denominator when coordinates missing). |

### Threshold Configuration (`app/config.py`)

- `DUPLICATE_SIMILARITY_THRESHOLD`: `0.75` (Composite threshold for candidate flagging)
- `STRONG_CANDIDATE_THRESHOLD`: `0.85`
- `SEMANTIC_STRONG_THRESHOLD`: `0.82`
- `SEMANTIC_CANDIDATE_THRESHOLD`: `0.70`
- `LOCATION_DISTANCE_THRESHOLD_KM`: `5.0` km radius

---

## 6. Model Specification

- **Model Name**: `BAAI/bge-small-en-v1.5`
- **Embedding Dimension**: 384 dimensions
- **Normalization**: L2 normalized unit vectors
- **Framework**: `sentence-transformers` / `PyTorch`

---

## 7. Configuration Settings

Configurable environment parameters (`app/config.py` / `.env.example`):

| Variable | Default Value | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | Pretrained embedding model identifier |
| `EMBEDDING_DIMENSION` | `384` | Dense vector dimension |
| `VECTOR_TOP_K` | `10` | Maximum candidate recommendations returned |
| `DUPLICATE_SIMILARITY_THRESHOLD` | `0.75` | Minimum composite score for duplicate boundary |
| `LOCATION_DISTANCE_THRESHOLD_KM` | `5.0` | Maximum location distance radius for decay |
| `SEMANTIC_WEIGHT` | `0.50` | Base weight for semantic vector similarity |
| `PRIMARY_DOMAIN_WEIGHT` | `0.15` | Base weight for primary domain match |
| `SUBCATEGORY_WEIGHT` | `0.15` | Base weight for subcategory match |
| `SECONDARY_DOMAIN_WEIGHT` | `0.10` | Base weight for secondary domain overlap |
| `LOCATION_WEIGHT` | `0.10` | Base weight for geographic proximity |

---

## 8. Running Independently

Start the service on **Port 8001**:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

- **Interactive API Documentation (Swagger UI)**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

---

## 9. API Specifications

### 9.1 GET `/health`
Exposes engine health and active embedding model metadata.

**Response**:
```json
{
  "status": "ok",
  "service": "CivicFix Duplicate Candidate Detection Engine",
  "embeddingModel": "BAAI/bge-small-en-v1.5",
  "embeddingDimension": 384,
  "duplicateThreshold": 0.75,
  "scoringVersion": "duplicate-v2"
}
```

---

### 9.2 POST `/duplicate-check`
Evaluates a target problem against candidate problems and returns ranked recommendations.

#### Request Contract (`DuplicateCheckRequest`)
```json
{
  "problem": {
    "problemId": "P-NEW-101",
    "title": "Severe water pipeline leak near central market",
    "description": "Drinking water pipeline has burst and clean water is flooding the street near central market.",
    "primaryDomain": "Water Resources",
    "subcategory": "Leakage",
    "secondaryDomains": ["Urban Infrastructure"],
    "location": {
      "district": "Patna",
      "state": "Bihar",
      "latitude": 25.5941,
      "longitude": 85.1376
    }
  },
  "candidates": [
    {
      "problemId": "P-EXISTING-501",
      "title": "Water main burst flooding market road",
      "description": "Clean drinking water leaking continuously from ruptured pipe on main market road.",
      "primaryDomain": "Water Resources",
      "subcategory": "Leakage",
      "secondaryDomains": [],
      "location": {
        "district": "Patna",
        "state": "Bihar",
        "latitude": 25.5945,
        "longitude": 85.1380
      }
    }
  ],
  "topK": 5
}
```

#### Successful Response Contract (`DuplicateCheckResponse`)
```json
{
  "problemId": "P-NEW-101",
  "status": "candidate_found",
  "duplicateCandidates": [
    {
      "candidateProblemId": "P-EXISTING-501",
      "duplicateScore": 0.9412,
      "semanticSimilarity": 0.925,
      "primaryDomainMatch": true,
      "subcategoryMatch": true,
      "secondaryDomainOverlap": 0.0,
      "locationDistanceKm": 0.06,
      "locationScore": 0.988,
      "candidateStatus": "strong_candidate",
      "signalStates": {
        "primaryDomain": "MATCH",
        "subcategory": "MATCH",
        "secondaryDomains": "AVAILABLE",
        "location": "AVAILABLE",
        "fingerprint": "AVAILABLE"
      },
      "scoreBreakdown": {
        "semantic": {"rawValue": 0.925, "state": "AVAILABLE", "weight": 0.5, "contribution": 0.4625, "used": true},
        "primaryDomain": {"rawValue": 1.0, "state": "MATCH", "weight": 0.15, "contribution": 0.15, "used": true},
        "subcategory": {"rawValue": 1.0, "state": "MATCH", "weight": 0.15, "contribution": 0.15, "used": true},
        "secondaryDomains": {"rawValue": 0.0, "state": "AVAILABLE", "weight": 0.1, "contribution": 0.0, "used": true},
        "location": {"rawValue": 0.988, "state": "AVAILABLE", "weight": 0.1, "contribution": 0.0988, "used": true}
      },
      "availableWeight": 1.0,
      "normalizedCompositeScore": 0.9412,
      "reasons": [
        "High semantic similarity (0.925)",
        "Primary domain match (Water Resources)",
        "Subcategory match (Leakage)",
        "Geographically very close (0.06 km)"
      ]
    }
  ],
  "scoringVersion": "duplicate-v2"
}
```

---

## 10. Testing

Run the automated test suite with `pytest`:

```bash
python -m pytest duplicate-detection/tests
```

**Verified Test Results**:
- **Total Tests**: 38 Passed, 0 Failed
- **Evaluation Dataset Matrix**: Evaluates candidate accuracy over 52 structured scenarios.

---

## 11. Integration Into Another Repository

To integrate the Duplicate Detection Engine into another application:

1. Treat this service as a stateless scoring microservice on **Port 8001**.
2. When a new problem is submitted to your backend, query your database for existing active problems in the same district/state (e.g. top 50 candidates).
3. Call `POST http://localhost:8001/duplicate-check` with the new problem and the candidate pool.
4. Persist or return the surfaced candidates in your platform's database and UI.

```text
Consuming Platform Backend
          │
          ├─► Fetch candidate problems from DB
          │
          ▼ POST http://localhost:8001/duplicate-check
Duplicate Detection Engine (:8001)
          │
          ▼ Returns candidates JSON with score breakdown
Consuming Platform Backend stores candidate links in local DB
```

---

## 12. Future Storage Architecture (Vector Database Extension)

| Aspect | Current Implementation | Future Production Possibilities |
|---|---|---|
| **Candidate Retrieval** | In-memory candidate array passed per payload | MongoDB Atlas Vector Search / Qdrant / Pinecone / FAISS index |
| **Embedding Cache** | Real-time generation per request payload | Pre-indexed vector embeddings stored in database |
| **Candidate Scope** | Explicit payload candidates array | Automated ANN (Approximate Nearest Neighbors) similarity search |

> **Note**: Future vector storage engines will be integrated as external indexing layers; the core `DuplicateDetector` scoring logic remains unchanged.

---

## 13. What NOT to Copy

When integrating this component:
- **DO NOT** copy or import internal Python modules (`app.services.duplicate_detector`, `app.services.embedding`) directly into your backend code.
- **DO NOT** embed vector model loading directly into your main application worker process.
- **DO NOT** allow the AI engine to own database persistence for problem records; database records belong strictly to the consuming application backend.
