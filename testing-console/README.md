# CivicFix — Development & Manual E2E Testing Console

An engineering QA & observability dashboard for manually testing the complete CivicFix problem lifecycle, AI microservices integration, state machine transitions, human reviewer actions, government routing, citizen timelines, and append-only audit logs.

---

## 1. Architecture Overview

```
                                [ Citizen / QA Engineer ]
                                           │
                                           ▼ (HTTP REST)
                 ┌───────────────────────────────────────────────────┐
                 │       CivicFix Main Backend                       │
                 │      (FastAPI @ Port 8002 / app)                  │
                 │  - Owns Problem Lifecycle & State Machine         │
                 │  - Enforces RBAC & Human-in-the-Loop             │
                 │  - Manages Versioning, Audits & Timeline          │
                 └─────────┬───────────────────────────────┬─────────┘
                           │                               │
           (HTTP REST)     │                               │     (HTTP REST)
                           ▼                               ▼
      ┌───────────────────────────────┐         ┌───────────────────────────────┐
      │ Classification Engine         │         │ Duplicate Detection Engine    │
      │ (FastAPI @ Port 8000)         │         │ (FastAPI @ Port 8001)         │
      │ - Taxonomy validation         │         │ - SentenceTransformers        │
      │ - Structured output rules     │         │   (BAAI/bge-small-en-v1.5)    │
      └──────────────┬────────────────┘         │ - Cosine similarity           │
                     │                          │ - Composite duplicate scoring │
                     ▼ (HTTP REST)              └───────────────────────────────┘
      ┌───────────────────────────────┐
      │ Ollama Server                 │
      │ (Port 11434)                  │
      │ - Gemma 3 4B Model            │
      └───────────────────────────────┘
```

---

## 2. Environment Variables

Create `.env` in the `testing-console/` directory (see `.env.example`):

```env
VITE_BACKEND_URL=http://localhost:8002
VITE_CLASSIFICATION_URL=http://localhost:8000
VITE_DUPLICATE_URL=http://localhost:8001
VITE_OLLAMA_URL=http://localhost:11434
```

Do **not** commit `.env` to Git.

---

## 3. Service Startup Commands

Run each of the 4 underlying backend services in separate terminal windows:

### 1. Ollama Inference Server
```powershell
ollama serve
# Ensure Gemma 3 4B weights are downloaded:
ollama pull gemma3:4b
```

### 2. AI Classification Engine (Port 8000)
```powershell
cd d:\CivicFix\classification-engine
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Duplicate Candidate Detection Engine (Port 8001)
```powershell
cd d:\CivicFix\duplicate-detection
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 4. CivicFix Main Backend Orchestrator (Port 8002)
```powershell
cd d:\CivicFix\backend
$env:PYTHONPATH="d:\CivicFix\backend"
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### 5. CivicFix E2E Testing Console Frontend (Port 5173)
```powershell
cd d:\CivicFix\testing-console
npm install
npm run dev
```

Open your browser to: `http://localhost:5173`

---

## 4. Testing Console Features & Views

1. **Dashboard**: Live status indicators for all 4 microservices, pending queue summary, and quick launch actions.
2. **System Health Probes**: Live HTTP ping probes to `/health` and `/health/dependencies` with millisecond latency metrics and customizable target URL overrides.
3. **Real Problem Test**: Interactive problem submission form (`POST /api/problems`) with 6 pre-loaded sample problem presets and live step-by-step pipeline execution tracking.
4. **Classification Lab**: Direct test bench for `/classify` on Port 8000 (Gemma 3 4B) to evaluate taxonomy mapping, severity, urgency, confidence, reasoning, and required expertise.
5. **Duplicate Detection Lab**: Dual problem comparator (Problem A vs Problem B) with 6 pre-loaded scenario presets to evaluate vector embedding similarity (`BAAI/bge-small-en-v1.5`), taxonomy overlap, and Haversine location distance.
6. **E2E Session Wizard**: Interactive step-by-step testing walkthrough guiding QA through a full session from problem submission → duplicate check → human review → government routing → timeline → audit log verification.
7. **Reviewer Queue**: Dashboard for `GET /api/reviewer/queue` surfacing flagged problems requiring human intervention (`confidence < 0.85` or duplicate candidate surfaced).
8. **Reviewer Actions**: Interactive forms for all 8 reviewer actions (`ACCEPT`, `CORRECT`, `MERGE_DUPLICATE`, `REQUEST_CLARIFICATION`, `REQUEST_VERIFICATION`, `REJECT_INVALID`, `REDIRECT`, `ESCALATE`). `CORRECT` creates a new reviewer `ProblemVersion` snapshot while preserving historical AI versions. `MERGE_DUPLICATE` links candidate to master without deleting original records.
9. **Government Routing**: Test form for `POST /api/government/{id}/route` targeting `GOVERNMENT`, `RESEARCH`, or `BOTH`.
10. **Citizen Timeline**: Visual chronological timeline renderer for `GET /api/problems/{id}/timeline` (verifying suppression of private reviewer notes).
11. **Append-Only Audit Log**: Log viewer for `GET /api/audit/{id}` displaying immutable audit trail events.
12. **Security & RBAC Matrix**: Matrix testing `X-User-Role` headers (`citizen`, `reviewer`, `admin`, `government_official`) against protected endpoints (verifying HTTP 403 Forbidden enforcement).
13. **Failure Isolation Testing**: Simulates microservice outages by pointing target URLs to invalid ports (e.g., `http://localhost:9999`) and verifying backend data preservation (`SUBMITTED` state retained, review flagged).
14. **Test History**: Local browser-side log manager saving manual execution records into `localStorage`.

---

## 5. Current Implementation Limitations

- **Database Storage**: The main backend's repositories fall back to temporary in-memory dictionaries if `motor` (async MongoDB driver) is missing.
- **Uninstantiated AI Analysis Model**: `AIAnalysisRecord` is defined in models but uninstantiated in intake.
- **Citizen Clarification Response**: No API endpoint currently exists for citizens to reply to clarification requests.
- **University Matching**: University matching logic is model-only / foundation-only.
- **Project Milestones & Notifications**: Not implemented.
