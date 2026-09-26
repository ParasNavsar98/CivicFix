# University Matching + Industry Marketplace Module — Implementation Plan

**Scope owner:** You
**Upstream (black box):** Friend 1's categorization AI
**Downstream/parallel (not our job):** Friend 2's main frontend/dashboard
**Status:** Planning only — no implementation code yet, per your instruction.

---

## 0. Restating Scope (so we don't drift)

**We own:**
- University capability data (MongoDB)
- Deterministic, explainable university matching/scoring
- Top-5 ranking
- Sequential assignment/acceptance workflow (SPOC accept/reject)
- Project handoff after acceptance
- Industry marketplace filtering (no AI, no ranking)
- Industry "Express Interest" → accept/reject → collaboration
- All backend/API/DB infra needed for the above
- A **minimal test frontend** (not the real product frontend) so we can demo/verify without waiting on Friend 2

**We do NOT touch:**
- Categorization AI / severity / urgency / confidence logic
- Duplicate detection
- Main frontend, navigation, auth UI, citizen/reviewer UI
- Government verification, citizen reporting
- An industry AI/recommendation engine

**Hard rule carried through the whole design:** `severity`, `urgency`, `confidence`, `governmentActionPossible` NEVER enter the university scoring formula. They may only be used (optionally) as a gate for *whether* matching runs at all — not *how well* a university scores.

---

## 1. Architecture

**Style:** Modular monolith (FastAPI + MongoDB), not microservices. One deployable service, cleanly separated internally by responsibility so it's independently testable and swappable later.

```
Categorization System (black box)
        │  approved structured problem JSON
        ▼
 [Categorization Adapter]  ← translation layer, the ONLY place that knows their schema
        ▼
 [Matching Engine]  → [University DB]
        ▼
 [Ranking] → [Assignment State Machine] → [University SPOC Accept/Reject]
        ▼
 [Project Handoff boundary] (stub — real project mgmt is someone else's system)

 [Marketplace Filter API] ← [Solutions Collection]
        ▼
 [Industry Express Interest] → [Accept/Reject] → [Collaboration]
```

Each box above = a `service` module in the backend, independently unit-testable, with no hidden cross-talk.

---

## 2. Folder Structure

```
backend/
├── app/
│   ├── main.py                      # FastAPI app, router registration
│   │
│   ├── config/
│   │   ├── settings.py              # env-driven config (Pydantic BaseSettings)
│   │   └── database.py              # Motor/PyMongo client, index creation on startup
│   │
│   ├── models/                      # Pydantic models = Mongo document shapes
│   │   ├── university.py
│   │   ├── matching.py
│   │   ├── assignment.py
│   │   ├── solution.py
│   │   ├── industry_interest.py
│   │   └── collaboration.py
│   │
│   ├── schemas/                     # request/response DTOs (separate from DB models)
│   │   ├── university.py
│   │   ├── problem_input.py
│   │   ├── matching.py
│   │   ├── assignment.py
│   │   ├── solution.py
│   │   └── marketplace.py
│   │
│   ├── services/
│   │   ├── matching_engine.py       # orchestrates the 7 scoring factors
│   │   ├── scoring/
│   │   │   ├── expertise.py
│   │   │   ├── faculty.py
│   │   │   ├── infrastructure.py
│   │   │   ├── past_projects.py
│   │   │   ├── geography.py
│   │   │   ├── capacity.py
│   │   │   └── industry_ecosystem.py
│   │   ├── ranking.py                # sort + top-5 + tie-break
│   │   ├── assignment_workflow.py    # state machine: SENT → ACCEPTED/REJECTED/TIMED_OUT
│   │   ├── marketplace.py            # filter-building for solutions
│   │   └── collaboration.py
│   │
│   ├── routers/
│   │   ├── universities.py
│   │   ├── matching.py
│   │   ├── assignments.py
│   │   ├── marketplace.py
│   │   ├── interests.py
│   │   └── collaborations.py
│   │
│   ├── integrations/
│   │   └── categorization_adapter.py # translates upstream JSON → our internal ProblemInput
│   │
│   ├── core/
│   │   ├── normalization.py          # lowercase/trim/synonym-map helpers (shared by scoring/)
│   │   └── auth.py                   # thin auth dependency, delegates to main system's token
│   │
│   └── tests/
│       ├── test_matching.py
│       ├── test_scoring_expertise.py
│       ├── test_scoring_faculty.py
│       ├── test_scoring_infrastructure.py
│       ├── test_scoring_past_projects.py
│       ├── test_scoring_geography.py
│       ├── test_scoring_capacity.py
│       ├── test_scoring_industry.py
│       ├── test_ranking.py
│       ├── test_assignment.py
│       ├── test_marketplace.py
│       └── test_collaboration.py
│
├── seed/
│   ├── universities.json
│   ├── problems.json
│   ├── solutions.json
│   └── industry_partners.json
│
├── requirements.txt
├── .env.example
└── README.md

frontend-test/                        # OUR minimal demo UI, not the real product frontend
├── index.html / a small Vite+React app (see §21)
```

Each scoring factor gets its **own file and own test file**. This is deliberate — it's your strongest demo point ("every score is independently testable, not a black box").

---

## 3. MongoDB Collections

| Collection | Purpose |
|---|---|
| `universities` | Capability profiles |
| `matching_results` | Snapshot of a full scoring run for a problem |
| `university_assignments` | Sequential assignment chain state |
| `solutions` | Published university solutions (marketplace listings) |
| `industry_partners` | Industry org profiles |
| `industry_interests` | Express-interest records |
| `collaborations` | Accepted interests → active collaborations |
| `matching_configuration` | Versioned, configurable scoring weights |
| `problems` *(optional, thin cache)* | Local read-only mirror of approved problem, only if categorization system doesn't push location reliably |

**Indexes to create on startup:**
- `universities`: `institution.location.district`, `institution.location.state`, `expertise`, `status`
- `solutions`: `domain`, `subcategory`, `location.state`, `location.district`, `developmentStage`, `supportNeeded`, `partnerType`, `status`, `visibility` (compound index candidate: `status + visibility + domain`)
- `university_assignments`: `problemId` (unique-per-active constraint enforced in code, see §8), `status`
- `industry_interests`: `solutionId`, `status`

---

## 4. University Profile Model

Matches the SRS-required fields exactly, per your README:

```
UniversityDocument
├── universityId: str (indexed, unique)
├── institution
│   ├── name, type
│   ├── location: { district, state, latitude, longitude }
│   └── contact: { email, phone }
├── departments: [str]
├── expertise: [str]
├── researchAreas: [str]
├── faculty: [FacultyEntry]
│     ├── facultyId, name, department
│     ├── expertise: [str]
│     ├── researchAreas: [str]
│     └── availableForProjects: bool
├── infrastructure: [str]
├── technologyCapabilities: [str]
├── pastProjects: [PastProject]
│     ├── title, domains: [str], expertise: [str], description
├── industryRelationships: [str]
├── capacity
│     ├── activeProjects: int
│     ├── maximumProjects: int
│     ├── availableTeams: int
│     └── availability: enum(AVAILABLE, LIMITED, UNAVAILABLE)
├── status: enum(ACTIVE, INACTIVE)
└── _demo: bool
```

CRUD via `POST/GET/PUT /api/universities` — no DELETE for MVP (soft-deactivate via `status`).

---

## 5. Categorization Integration Boundary (`categorization_adapter.py`)

This is the **only file allowed to know the upstream JSON shape**. Its job: convert the friend's output into our internal, stable `ProblemInput` model.

```
ProblemInput (our internal, stable contract)
├── problemId: str
├── primaryDomain: str
├── secondaryDomains: [str]
├── subcategory: str
├── requiredExpertise: [str]
├── requiredResources: [str]
├── location: { district, state, lat?, lng? }   ← from problem record, NOT categorization
├── researchRequired: bool        (gate only, never scored)
└── governmentActionPossible: bool (gate only, never scored)
```

Explicitly dropped/never forwarded into scoring: `severity`, `severityAssessment`, `urgency`, `confidence`, `peopleAffected`, `reasoning`.

If the real categorization system isn't wired up yet, the adapter can accept a raw dict matching their documented schema and a mock/local `problems` lookup for location — this lets us build and test end-to-end without waiting on Friend 1.

---

## 6. Matching Engine & Scoring Formulas

Each factor returns a float in `[0.0, 1.0]`, plus a small explanation payload (matched items, reasoning string). The engine just runs all 7, applies weights, and returns a `MatchingResult`.

### 6.1 Expertise Match (35%)
- Normalize both `requiredExpertise` and `university.expertise + university.researchAreas`: lowercase → trim → strip punctuation → pass through a small **synonym/alias dictionary** (e.g. `"env management" == "environmental management"`), config-driven, stored as a JSON/dict we can extend without touching code.
- `score = |matched| / |required|` (capped at 1.0)
- Explanation: list of matched terms + list of unmatched required terms.

### 6.2 Faculty Expertise (20%)
- Same normalization, compared against `faculty[].expertise + faculty[].researchAreas`, filtered to `availableForProjects == true` only.
- `score = |required terms with ≥1 matching faculty| / |required|`
- Explanation: matched faculty IDs + which required expertise each one covers.

### 6.3 Infrastructure Match (15%)
- Compare `requiredResources` against `infrastructure + technologyCapabilities`.
- Same normalization approach.
- `score = |matched resources| / |required resources|`

### 6.4 Relevant Past Projects (10%)
- Compare `primaryDomain + secondaryDomains + subcategory + requiredExpertise` against each `pastProjects[].domains + .expertise`.
- A project "counts" if it has ≥1 overlapping domain OR ≥1 overlapping expertise term.
- `score = min(matchedProjectCount / 2, 1.0)` — i.e. 2+ relevant past projects = full score (configurable divisor, not hardcoded "2" forever — put it in `matching_configuration`).

### 6.5 Geographic Relevance (10%) — deterministic table
| Condition | Score |
|---|---|
| Same district | 1.0 |
| Same state, different district | 0.6 |
| Different state | 0.2 |

### 6.6 Current Capacity (5%) — explicit edge-case handling
```
if availability == UNAVAILABLE: score = 0.0
elif maximumProjects == 0: score = 0.0            # explicit edge case
elif activeProjects >= maximumProjects: score = 0.0
else:
    freeRatio = (maximumProjects - activeProjects) / maximumProjects
    if availability == LIMITED: freeRatio *= 0.5    # LIMITED caps upside
    score = min(freeRatio, 1.0)
```
This resolves the exact "invalid capacity" edge cases your README flags: zero max, active > max, and the 3-state enum all get deterministic, testable behavior instead of silently guessed logic.

### 6.7 Industry Ecosystem Relevance (5%)
- Simple presence check: does `university.industryRelationships` contain any term related to the problem's domain (via a small domain→industry-keyword map, e.g. "Environment" → "Environmental Technology")?
- `score = 1.0` if any match, else `0.3` (baseline, not zero — having *some* industry relationships is weakly positive even without an exact domain hit), `0.0` if the list is empty. This mapping lives in config, not hardcoded logic sprawl.

### 6.8 Final Score
```
final = (expertise*0.35 + faculty*0.20 + infrastructure*0.15
        + pastProjects*0.10 + geography*0.10 + capacity*0.05
        + industry*0.05) * 100
```

---

## 7. Configuration Design (`matching_configuration` collection)

```json
{
  "configId": "default",
  "version": 1,
  "weights": {
    "expertise": 0.35, "faculty": 0.20, "infrastructure": 0.15,
    "pastProjects": 0.10, "geography": 0.10, "capacity": 0.05, "industry": 0.05
  },
  "pastProjectsDivisor": 2,
  "synonymDictionary": { "environmental management": ["env management", "environment mgmt"] },
  "activeSince": "..."
}
```
- Loaded once per matching run and **stamped into the result's snapshot** (see §9) so historical scores stay explainable even if weights change later.
- MVP: single active config, editable via a protected endpoint or direct seed update. SHOULD HAVE: versioned configs with `activeSince` so we can audit "what weights were active on date X."

---

## 8. Ranking & Top-5 Selection

1. Fetch all `status: ACTIVE` universities.
2. Run matching engine per university → `MatchingResult`.
3. Sort descending by `finalScore`.
4. **Tie-break rule (deterministic):** on equal `finalScore`, sort by `expertise` factor score desc, then `universityId` asc (guarantees stable, reproducible ordering — no `sort()` randomness).
5. Take top 5, assign `rank: 1..5`.
6. Persist the full ranked list to `matching_results` (not just top 5) — useful for debugging/demo ("why wasn't university X in the top 5").

---

## 9. Sequential Assignment State Machine

**States:** `PENDING → SENT → (ACCEPTED | REJECTED | TIMED_OUT | CANCELLED)`

```
create_assignment_chain(problemId, top5):
    assert no existing ACTIVE chain for problemId   # prevents duplicates
    create Assignment(rank=1, status=SENT, deadline=now+defaultHours)
    (ranks 2-5 stored as PENDING, not yet sent)

on university action / scheduler tick:
    if assignment.status == SENT and now >= assignment.deadline:
        assignment.status = TIMED_OUT
        activate_next_rank()

    if SPOC accepts:
        assignment.status = ACCEPTED
        cancel all other PENDING assignments for this problemId
        trigger handoff (§11)

    if SPOC rejects (reason required):
        assignment.status = REJECTED
        activate_next_rank()

activate_next_rank():
    next = find next PENDING assignment for problemId by rank
    if next: next.status = SENT; next.deadline = now + defaultHours
    else: mark problem as "no university accepted" (needs manual/admin review — FUTURE: escalation flow)
```

**Deadline persistence rule (explicit, per your README):**
`assignment.deadline` is computed and stored **at creation time** using whatever the default is *then*. Changing `matching_configuration.defaultDeadlineHours` later never touches existing assignments — only future ones.

**Reminder:** optional background check `now >= deadline - reminderWindow` → sets `reminderSent = true`, sends notification (stub for MVP — actual notification channel is out of scope/TBD). Reminder is purely additive and never gates the timeout check.

**Scheduler mechanism (MVP-appropriate):** a simple periodic job (APScheduler or a cron-triggered endpoint) that scans `SENT` assignments past deadline. No Kafka/queues needed at this scale.

---

## 10. Assignment Document Shape

```json
{
  "assignmentId": "ASN-001",
  "problemId": "JH-2026-001245",
  "universityId": "UNI-JH-001",
  "rank": 1,
  "status": "SENT",
  "score": 91.2,
  "scoreSnapshot": { "expertise": 0.92, "faculty": 0.88, "...": "..." },
  "sentAt": "...",
  "deadline": "...",
  "reminderSent": false,
  "respondedAt": null,
  "response": null,
  "rejectionReason": null
}
```

---

## 11. University Acceptance & Handoff Boundary

SPOC-facing endpoints only need to expose: the problem summary, the matching explanation, and accept/reject actions. On accept:
1. Mark assignment `ACCEPTED`.
2. Cancel sibling assignments.
3. Call a `handoff` function that emits a clean payload (`problemId`, `universityId`, `assignmentId`, `scoreSnapshot`) — **this is the API boundary**, not an implementation of project management itself. For MVP this can just create a minimal `projects` stub record or return the payload to whatever system consumes it next; we are explicitly not building the full project-management platform.

---

## 12. Industry Marketplace (no scoring, no ranking — just filters)

`GET /api/marketplace/solutions` — all filters optional, combinable, server-side, MongoDB `$and` query built dynamically only from the params actually present:

```
?domain=Agriculture&subcategory=Pest%20Management&state=Jharkhand
&district=Ranchi&developmentStage=PROTOTYPE&supportNeeded=Hardware&partnerType=Startup
```

`supportNeeded`/`partnerType` are arrays on the document → query uses `$in` or `$all` depending on desired semantics (recommend `$in`: "solution needs at least one of the requested support types" — more useful for browsing than requiring all).

Only `status: PUBLISHED` and `visibility: PUBLIC` solutions are ever returned by this endpoint.

---

## 13. Industry Interest & Collaboration Workflow

```
Industry views solution → POST /api/marketplace/{solutionId}/interest
    → creates industry_interests doc, status=PENDING
    → duplicate check: same partnerId + solutionId + status=PENDING → reject with 409

University/project owner reviews:
    POST /api/interests/{interestId}/accept → status=ACCEPTED, create collaboration (status=ACTIVE)
    POST /api/interests/{interestId}/reject → status=REJECTED, rejectionReason stored

Authorization: only the owning university's authorized user (validated via §14) may accept/reject.
```

---

## 14. Authorization Boundary

We do **not** build a second auth system. We consume whatever token/session the main platform issues (JWT assumed, since that's the common pattern with the stated Node/Express-adjacent SRS baseline).

- `core/auth.py` exposes a single FastAPI dependency, e.g. `get_current_user()`, that decodes/validates a bearer token using a shared secret/JWKS URL provided via env config.
- Role checks (e.g. "is this user the SPOC for university X," "is this user authorized to act for solution Y's owner") happen in our routers, using `role`/`universityId`/`orgId` claims we expect to be present on the token.
- **Until real auth is wired up:** a `DEV_MODE` env flag lets us pass identity via a header/query param for local testing, clearly logged as dev-only and disabled by default.

---

## 15. Solution Document Shape (marketplace-facing subset)

```json
{
  "solutionId": "SOL-001", "problemId": "JH-001", "projectId": "PRJ-001", "universityId": "UNI-001",
  "title": "Smart Pest Migration Detection System",
  "domain": "Agriculture", "subcategory": "Pest Management",
  "location": { "state": "Jharkhand", "district": "Ranchi" },
  "developmentStage": "PROTOTYPE",
  "supportNeeded": ["Hardware", "Technical Mentorship", "Testing"],
  "partnerType": ["Startup", "Industry"],
  "visibility": "PUBLIC", "status": "PUBLISHED"
}
```
We own only the fields needed for filtering/display; the richer solution content (full write-up, attachments) can live elsewhere or as extra fields we simply pass through without modeling deeply.

---

## 16. API Surface (full list)

| Area | Endpoint | Method |
|---|---|---|
| Universities | `/api/universities` | GET, POST |
| | `/api/universities/{id}` | GET, PUT |
| Matching | `/api/matching/{problemId}` | POST (run), GET (fetch stored result) |
| | `/api/universities/matches/{problemId}` | GET (SRS-named alias, top-5 view) |
| Assignments | `/api/assignments/{problemId}` | GET |
| | `/api/assignments/{assignmentId}` | GET |
| | `/api/assignments/{assignmentId}/accept` | POST |
| | `/api/assignments/{assignmentId}/reject` | POST |
| Marketplace | `/api/marketplace/solutions` | GET |
| | `/api/marketplace/solutions/{solutionId}` | GET |
| Interests | `/api/marketplace/{solutionId}/interest` | POST |
| | `/api/solutions/{solutionId}/interests` | GET |
| | `/api/interests/{interestId}/accept` | POST |
| | `/api/interests/{interestId}/reject` | POST |
| Collaboration | `/api/collaborations` | GET |
| | `/api/collaborations/{id}` | GET |

---

## 17. Seed / Demo Data Plan

- 10 universities, deliberately differentiated (per your README's A/B/C/D example) so different problems produce visibly different rankings — this is your best demo moment.
- 5–10 sample `ProblemInput`-shaped records (mimicking categorization output) covering different domains.
- 10–20 solutions spread across domains/stages/support types, so marketplace filters have something to actually filter.
- 5 industry partners.
- Every seed record tagged `"_demo": true`; a startup check can refuse to seed twice / warn if demo data exists in what looks like a prod DB.

---

## 18. Testing Strategy

Unit tests, one file per scoring factor, using **fixed, hand-computed** input/output pairs (not random data) so failures are meaningful:
- Expertise: full match / partial / zero match / synonym-normalized match
- Faculty: match / no available faculty / faculty exists but not `availableForProjects`
- Infrastructure: full / partial / none
- Geography: same district / same state / different state
- Capacity: available / limited / unavailable / `maximumProjects=0` / `activeProjects > maximumProjects`
- **Weighted score**: one fully manually-verified example (like your README's 86.4 example) — this becomes your regression anchor.
- Ranking: 10 universities → correct descending order, correct top-5, deterministic tie-break
- Assignment: accept / reject→next / timeout→next / all reject / all timeout / duplicate-active-chain prevention
- Deadline: changing default config doesn't mutate existing assignment deadlines
- Marketplace: single filter / combined filters / no-result case
- Industry: interest creation / duplicate interest rejected / accept → collaboration created / reject stores reason / unauthorized accept attempt blocked

Target: pytest, run via `pytest backend/app/tests`, using `mongomock` or a spun-up local MongoDB test container so tests don't touch real data.

---

## 19. Local Dev Setup & Deployment

- **Local:** `docker-compose.yml` with `mongo` + `backend` services; `.env.example` documents required vars (`MONGO_URI`, `JWT_SECRET`/`JWKS_URL`, `DEFAULT_ASSIGNMENT_DEADLINE_HOURS`, `DEV_MODE`).
- Startup script seeds demo data if the `universities` collection is empty and `SEED_ON_STARTUP=true`.
- **Deployment:** any container host works (Render/Railway/Fly.io for a hackathon demo, or whatever the main project already uses) + MongoDB Atlas free tier. No infra beyond that is needed — explicitly no Kafka/Redis/Kubernetes per your README's own constraint.

---

## 20. How Teammates' Frontend Consumes This

- Clean REST/JSON, documented via FastAPI's auto-generated OpenAPI/Swagger (`/docs`) — Friend 2 can explore and integrate without us writing separate API docs by hand.
- CORS enabled for their frontend origin via config.
- Every response uses consistent envelope shape (e.g. `{ data, error }`) so their frontend error-handling is uniform across our endpoints.

---

## 21. Minimal Test Frontend (our own, throwaway)

Since we need to demo without waiting on Friend 2's real frontend, a small single-page app (plain HTML/JS or a tiny Vite+React app) covering just enough to prove the pipeline works:
- A form to submit a mock `ProblemInput` (or pick a seeded sample problem) → shows top-5 ranked universities with score breakdown.
- A "SPOC view" to accept/reject the current assignment for a problem.
- A marketplace browser with filter dropdowns → results list.
- An "express interest" button + a simple accept/reject panel.

This is a **development/demo tool**, not a deliverable to merge into the real product frontend.

---

## 22. MVP vs SHOULD HAVE vs FUTURE

**MUST HAVE (MVP):**
University CRUD · all 7 scoring factors · configurable weights (single active config) · top-5 ranking with deterministic tie-break · sequential assignment with timeout · accept/reject with handoff stub · marketplace filtering · express interest · accept/reject → collaboration · full unit test suite · seed data · minimal test frontend.

**SHOULD HAVE:**
Versioned matching configs with audit history · reminder notifications (even just logged/emailed) · admin endpoint to edit weights safely · pagination on list endpoints · basic rate limiting.

**FUTURE/OPTIONAL:**
Escalation flow when all 5 universities reject/timeout · analytics on match quality vs. actual outcomes · richer synonym dictionary (semantic, still non-LLM) · multi-language expertise terms · webhook notifications instead of polling.

---

## 23. End-to-End Example Flow

1. Categorization system approves a problem → adapter converts to `ProblemInput`.
2. `POST /api/matching/{problemId}` → engine scores all active universities → stores full ranked list in `matching_results`, returns top 5.
3. Assignment chain created; University A (`rank 1`) gets `status: SENT`, 48h deadline.
4. University A's SPOC calls `GET` to view the explanation, then `POST /accept`.
5. Assignment marked `ACCEPTED`; other 4 cancelled; handoff payload emitted.
6. Later, University A publishes a `solution` linked to that project.
7. Industry user filters marketplace by domain+state → finds it → `POST interest`.
8. University reviews interest → `POST accept` → `collaboration` created, `status: ACTIVE`.

---

## Open Questions Before We Start Coding

1. **Auth:** do you already know the token format (JWT claims) Friend 2's auth system issues, or should we build against a mocked token for now and adjust later?
2. **Deadline scheduler:** background job (APScheduler) vs. a cron-hit endpoint vs. lazy check-on-read (only evaluate timeout when someone GETs the assignment)? Lazy check is simplest for a hackathon and avoids running a scheduler process at all.
3. **Test frontend:** plain HTML+JS (fastest) or a small React app (nicer if you want to reuse components later)?

Once you confirm these three, we start writing code — starting with models → scoring factors (with tests) → matching engine → API layer, in that order.
