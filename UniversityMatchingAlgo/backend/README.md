# University Matching + Industry Marketplace Module

Backend for the SIH "Societal Innovation Collaboration Portal" — the university
matching, sequential assignment, and industry marketplace/collaboration slice
of the project. Consumes the categorization system as a black box.

See `../university-matching-module-plan.md` (shared earlier) for the full
design rationale. This README is just "how do I run it."

## 1. Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## 2. Database

**For local development right now:** run a local MongoDB instance, e.g.:

```bash
docker run -d -p 27017:27017 --name matching-mongo mongo:7
```

`.env`'s default `MONGO_URI=mongodb://localhost:27017` will just work against that.

**Later, connecting to MongoDB Atlas (cloud):** change ONE line in `.env`:

```
MONGO_URI=mongodb+srv://<user>:<password>@<your-cluster>.mongodb.net
```

Nothing else in the codebase needs to change — `app/config/database.py` is the
only file that reads this value.

## 3. Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

- Swagger/OpenAPI docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

On first startup (empty `universities` collection + `SEED_ON_STARTUP=true`),
demo data is loaded automatically: 6 universities, 8 solutions, 5 industry
partners, all tagged `"_demo": true`. See `seed/` to add more — follow the
existing pattern in `seed/universities.json` and keep capabilities
deliberately different across universities so matching produces meaningfully
different rankings.

To reseed manually: `python -m seed.seed_db`

## 4. Run the tests

```bash
pytest app/tests/ -v
```

55 tests, all using `mongomock` (no real database needed to run them) — see
`app/tests/conftest.py`. Every scoring factor, the weighted final score
(with one fully hand-verified example), ranking/tie-breaks, the full
sequential assignment state machine (accept / reject-cascade /
timeout-cascade / duplicate-chain prevention), marketplace filtering, and
the industry interest → collaboration workflow are covered.

## 5. Run the test frontend

This is a throwaway dev/demo tool — NOT the real product frontend (that's
your teammate's job). It's plain HTML/JS, talking directly to the API.

```bash
cd ../frontend-test
python3 -m http.server 5500
```

Then open http://localhost:5500 in a browser. The backend's default
`CORS_ORIGINS` in `.env.example` already allows `http://localhost:5500`.

Walk-through:
1. Pick a sample problem (or paste your own classification JSON) → **Run Matching**
   → shows the top-5 ranked universities and creates the assignment chain.
2. **Assignment Chain** section shows rank/status — Accept or Reject the
   currently-`SENT` one and watch the chain advance.
3. **Industry Marketplace** — filter and browse published solutions.
4. **Express Interest** on a solution, then Accept/Reject as the owning
   university (set "Acting as University ID" to match the solution's
   `universityId`, e.g. `UNI-JH-001` for `SOL-001`) → creates a collaboration.

## 6. Connecting the real categorization system

`app/integrations/categorization_adapter.py` is the ONLY file that knows the
categorization system's JSON shape. When your teammate's system is live,
whatever calls `POST /api/matching/{problemId}` just needs to supply:
- `classification`: their exact classification JSON (as documented in their README)
- `location`: `{district, state, latitude?, longitude?}` from the original
  problem record — the classifier doesn't provide location, so this must come
  from wherever problems are stored.

Severity, urgency, confidence, and peopleAffected are read by nothing in the
scoring path — verify this stays true if you ever touch the adapter.

## 7. Auth

`DEV_MODE=true` (default) lets you pass identity via `X-Dev-User-Id` /
`X-Dev-Role` headers instead of a real JWT — this is what the test frontend
uses for the industry-interest accept/reject flow, which needs to know
"which university is this." Set `DEV_MODE=false` and configure `JWT_SECRET`
once the main platform's real auth is available.

## 8. What's NOT built here (by design)

Real project-management platform, citizen frontend, categorization AI,
industry-side AI/ranking, government verification. See the shared plan
document for the full scope boundary.
