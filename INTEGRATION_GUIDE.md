# CivicFix — Cross-Repository Integration & Modular Architecture Guide

This document explains how to extract, integrate, and reuse the independent components of **CivicFix** into other software repositories and platform architectures.

---

## 1. Modular Architecture Overview

CivicFix is designed as a set of independently deployable microservices and frontends:

```text
                    ┌──────────────────────┐
                    │   Consumer Backend   │
                    └──────────┬───────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
                  ▼                         ▼
        Classification Engine      Duplicate Detection
             :8000                       :8001
                  │                         │
                  ▼                         ▼
              Ollama                 Embedding Model
           (Gemma 3 4B)          (bge-small-en-v1.5)


                 Testing Console
                       │
            ┌──────────┼──────────┐
            ▼          ▼          ▼
          :8000      :8001      :8002
```

---

## 2. Core Architectural Principles

1. **Contract-Based HTTP REST Integration**:
   Consuming repositories integrate with CivicFix components strictly via documented HTTP REST API contracts (`POST /classify`, `POST /duplicate-check`). Consuming backends MUST NOT import internal Python files or couple directly to microservice source code.

2. **Domain Model & Database Ownership**:
   The consuming application backend owns its database, problem persistence models, user accounts, and workflows. CivicFix AI services are stateless processors that do not persist problem records.

3. **Human-in-the-Loop Authority**:
   AI microservices provide recommendations, confidence scores, and explainable evidence. Consequential actions (such as merging duplicate problems or approving AI classifications) MUST remain under human reviewer control.

---

## 3. Independent Components Summary

### 3.1 AI Classification Engine (`classification-engine/`)
- **Port**: `8000`
- **Main API**: `POST /classify`
- **Health**: `GET /health`
- **Purpose**: Structures unstructured problem reports into 12 controlled taxonomy domains, severity factors, urgency ratings, and required resources.
- **Integration**: Call `POST http://<host>:8000/classify` during problem creation in your platform's intake pipeline.

### 3.2 Duplicate Candidate Detection Engine (`duplicate-detection/`)
- **Port**: `8001`
- **Main API**: `POST /duplicate-check`
- **Health**: `GET /health`
- **Purpose**: Generates 384-dimensional dense vector embeddings (`BAAI/bge-small-en-v1.5`), evaluates multi-factor signal similarity, and ranks candidate duplicates.
- **Integration**: Query your database for candidate active problems in the same district/state, then pass them to `POST http://<host>:8001/duplicate-check`.

### 3.3 Testing Console & Integration UI (`testing-console/`)
- **Port**: `5173`
- **Purpose**: React/TypeScript engineering console for monitoring health, testing AI services, running E2E QA sessions, exercising reviewer actions, and inspecting audit logs.
- **Integration**: Can be run standalone or its component views (`src/views/`, `src/api/`) can be copied into an administrative portal.

---

## 4. Integration Checklist for External Repositories

### Integrating Classification Engine
- [ ] Run local Ollama server and pull model: `ollama pull gemma3:4b`
- [ ] Start Classification Engine service: `cd classification-engine && uvicorn app.main:app --port 8000`
- [ ] Configure consuming backend `CLASSIFICATION_ENGINE_URL=http://localhost:8000`
- [ ] Send `POST /classify` during problem intake
- [ ] Store returned `primaryDomain`, `subcategory`, `secondaryDomains`, `severity`, and `confidence` in your platform's DB

### Integrating Duplicate Detection Engine
- [ ] Install PyTorch & Sentence Transformers dependencies (`requirements.txt`)
- [ ] Start Duplicate Detection service: `cd duplicate-detection && uvicorn app.main:app --port 8001`
- [ ] Configure consuming backend `DUPLICATE_DETECTION_URL=http://localhost:8001`
- [ ] Send `POST /duplicate-check` with new problem and candidate list
- [ ] Store candidate links and score breakdowns for human reviewer inspection

---

## 5. Directory Boundary Rules

When copying or extracting components into a new repository:

- **Component A (Classification Engine)**: Copy `classification-engine/`. Do NOT copy `duplicate-detection/` or `testing-console/`.
- **Component B (Duplicate Detection Engine)**: Copy `duplicate-detection/`. Do NOT copy `classification-engine/` or `testing-console/`.
- **Component C (Testing Console)**: Copy `testing-console/`. Do NOT copy backend Python files into the frontend build pipeline.
