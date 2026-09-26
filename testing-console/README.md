# CivicFix Testing Console

Developer QA, observability, and interactive demonstration testing console built with **React**, **TypeScript**, **Vite**, and **Tailwind CSS**.

---

## 1. Purpose

The **CivicFix Testing Console** is a specialized frontend application designed for developers, QA engineers, and reviewers. It provides an intuitive suite of 14 interactive views to test the complete CivicFix lifecycle: submitting problems, inspecting raw AI microservice responses, evaluating duplicate detection scoring, running end-to-end QA pipelines, exercising human reviewer actions, inspecting citizen timelines, and verifying audit trails.

---

## 2. Technology Stack

- **Framework**: React 19
- **Build Tool**: Vite 8
- **Language**: TypeScript 6
- **Styling**: Tailwind CSS v4
- **Icons**: Lucide React (`lucide-react`)
- **Linter**: Oxlint (`oxlint`)

---

## 3. Project Structure

```text
testing-console/
├── src/
│   ├── main.tsx                  # React application entry point
│   ├── App.tsx                   # Main layout, navigation sidebar, & view router
│   ├── App.css                   # Global styles
│   ├── index.css                 # Tailwind CSS imports
│   ├── config.ts                 # Centralized service URL configuration & localStorage overrides
│   ├── types.ts                  # Shared TypeScript data types & API interfaces
│   │
│   ├── api/                      # API client service layer
│   │   ├── backend.ts            # Main Backend Orchestrator client (:8002)
│   │   ├── classification.ts     # Classification Engine client (:8000)
│   │   ├── duplicate.ts          # Duplicate Detection Engine client (:8001)
│   │   └── ollama.ts             # Direct Ollama API client (:11434)
│   │
│   ├── components/               # Reusable UI components
│   │   ├── Header.tsx            # Top status bar & environment switcher
│   │   ├── Sidebar.tsx           # Navigation menu bar
│   │   ├── StatusBadge.tsx       # Standardized status badge pill
│   │   ├── TestResultBadge.tsx   # Pass/Fail test indicator
│   │   ├── JsonViewer.tsx        # Syntax-highlighted JSON viewer
│   │   └── RequestResponseInspector.tsx # Raw HTTP payload inspector
│   │
│   └── views/                    # 14 Interactive QA testing views
│       ├── DashboardView.tsx               # System overview & live service probes
│       ├── SystemHealthView.tsx            # Microservice health probe test bench
│       ├── RealProblemTestView.tsx         # Problem submission test form with presets
│       ├── ClassificationLabView.tsx       # Direct /classify testing bench (:8000)
│       ├── DuplicateDetectionLabView.tsx   # Dual problem comparator bench (:8001)
│       ├── E2EPipelineView.tsx             # Guided step-by-step QA session wizard
│       ├── ReviewerQueueView.tsx           # Human review queue inspector
│       ├── ReviewerActionsView.tsx         # 8 human-in-the-loop action controls
│       ├── GovernmentRoutingView.tsx       # Department routing test bench
│       ├── TimelineView.tsx                # Citizen public timeline inspector
│       ├── AuditView.tsx                   # Immutable append-only audit log viewer
│       ├── SecurityRbacView.tsx            # Role-based access control test matrix
│       ├── FailureTestingView.tsx          # Microservice outage simulation bench
│       └── TestHistoryView.tsx             # Local execution history manager
│
├── public/                       # Static public assets (icons, favicon)
├── package.json                  # Node.js dependencies & scripts
├── vite.config.ts                # Vite configuration & development API proxies
├── tsconfig.json                 # TypeScript compiler configuration
└── README.md                     # Component documentation
```

---

## 4. Service Port Mapping & Dependencies

The Testing Console communicates with 4 underlying services:

| Service Name | Port | Base URL Variable | Description |
|---|---|---|---|
| **Classification Engine** | `8000` | `VITE_CLASSIFICATION_URL` | Standalone AI Classification FastAPI Service |
| **Duplicate Detection Engine** | `8001` | `VITE_DUPLICATE_URL` | Standalone Duplicate Candidate Detection FastAPI Service |
| **CivicFix Backend Orchestrator** | `8002` | `VITE_BACKEND_URL` | Main Application Backend Service |
| **Ollama Local Server** | `11434` | `VITE_OLLAMA_URL` | Local LLM Inference Engine (Gemma 3 4B) |
| **Testing Console (UI)** | `5173` | `http://localhost:5173` | React/Vite Frontend Application |

---

## 5. Running the Console

1. **Navigate to testing-console**:
   ```bash
   cd testing-console
   ```

2. **Install Node Dependencies**:
   ```bash
   npm install
   ```

3. **Start Development Server**:
   ```bash
   npx vite --host 127.0.0.1 --port 5173 --strictPort
   ```
   Or run:
   ```bash
   npm run dev
   ```

4. **Access UI**: Open `http://localhost:5173` in your browser.

---

## 6. Environment Configuration

Copy `.env.example` to `.env`:
```env
VITE_BACKEND_URL=http://localhost:8002
VITE_CLASSIFICATION_URL=http://localhost:8000
VITE_DUPLICATE_URL=http://localhost:8001
VITE_OLLAMA_URL=http://localhost:11434
```

> **Note**: Service URLs can also be dynamically configured directly from the UI header ("System Settings") without restarting the development server (overrides stored in `localStorage`).

---

## 7. Available QA Views & Features

1. **Dashboard**: High-level system overview with real-time status indicators for all 4 microservices.
2. **System Health**: Detailed health probes (`/health`) with latency metrics and customizable target URL overrides.
3. **Real Problem Test**: Interactive problem submission form with 6 pre-loaded sample problem presets.
4. **Classification Lab**: Test bench targeting `POST http://localhost:8000/classify` to inspect taxonomy, severity, urgency, confidence, and reasoning.
5. **Duplicate Detection Lab**: Comparator bench targeting `POST http://localhost:8001/duplicate-check` with 6 scenario presets evaluating vector similarity, signal states, and score breakdowns.
6. **E2E Pipeline**: Guided step-by-step session wizard leading QA through problem creation -> duplicate check -> human review -> routing -> timeline -> audit.
7. **Reviewer Queue**: Inspector surfacing flagged problems requiring human intervention (`confidence < 0.85` or duplicate candidate found).
8. **Reviewer Actions**: Interactive controls for all 8 human-in-the-loop actions (`ACCEPT`, `CORRECT`, `MERGE_DUPLICATE`, `REQUEST_CLARIFICATION`, `REQUEST_VERIFICATION`, `REJECT_INVALID`, `REDIRECT`, `ESCALATE`).
9. **Government Routing**: Test form for routing problems to government departments or research institutions.
10. **Citizen Timeline**: Chronological event viewer verifying that private reviewer notes are suppressed from public view.
11. **Append-Only Audit Log**: Viewer for immutable audit trail events.
12. **Security / RBAC Matrix**: Security matrix exercising `X-User-Role` headers (`citizen`, `reviewer`, `admin`, `government_official`) against protected endpoints.
13. **Failure Testing**: Simulates microservice outages by pointing target URLs to invalid ports to test backend fallback behavior.
14. **Test History**: Local execution log manager saving test runs into browser `localStorage`.

---

## 8. Integration Into Another Repository

The Testing Console frontend is modularly organized and can be adapted into another platform's developer dashboard or administrative UI:

- **API Layer (`src/api/`)**: Decoupled HTTP client modules using standard `fetch` API.
- **Type Definitions (`src/types.ts`)**: Clean TypeScript interfaces mapping to backend API contracts.
- **Reusable UI Components (`src/components/`)**: Standalone React components (`JsonViewer`, `StatusBadge`, `RequestResponseInspector`).

---

## 9. Current Status & Limitations

- **Implemented Features**: All 14 views, microservice health probing, direct AI service labs, reviewer action forms, and audit trail viewers are fully implemented.
- **Backend Fallback**: In-memory repository fallback mode when MongoDB is not running.
- **Placeholder / Foundation-Only Features**: Citizen clarification response form, automated notification dispatch, and university matching modules are defined in models/UI as foundation placeholders.
