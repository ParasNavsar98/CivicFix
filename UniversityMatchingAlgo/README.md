# University Matching + Industry Marketplace Module

A FastAPI + MongoDB backend for the SIH university matching, sequential assignment, and industry marketplace workflow. The project matches universities to social-impact problem requirements, ranks the best-fit institutions, manages assignment state transitions, and supports industry interest + collaboration flows.

This repo includes:
- a backend API for matching, assignment, marketplace, and collaboration logic
- seed data for demo universities, solutions, and industry partners
- a lightweight browser-based test frontend for local validation and demos
- a full pytest suite covering scoring, ranking, assignment workflow, marketplace filters, and collaboration logic

## Tech stack

- Python 3.11+
- FastAPI
- Pydantic + Pydantic Settings
- PyMongo
- MongoDB Atlas or local MongoDB
- pytest
- HTML/JavaScript demo frontend

## Project structure

```text
project-root/
├── IMPLEMENTATION_PLAN.md
├── README.md
├── .gitignore
├── backend/
│   ├── .env.example
│   ├── .env
│   ├── README.md
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── config/
│   │   ├── core/
│   │   ├── integrations/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── tests/
│   └── seed/
├── frontend-test/
│   ├── index.html
│   └── app.js
└──
```

## Features

- University matching against problem requirements and capabilities
- Deterministic score calculation across multiple factors
- Top-5 ranking and tie-break logic
- Sequential assignment workflow for university SPOC decisions
- Industry marketplace listing and filtering
- Express-interest workflow and collaboration creation
- MongoDB-backed persistence with startup indexes and seeding

## Architecture summary

The backend follows a modular monolith structure:

- `app/main.py` initializes the FastAPI app and routers
- `app/config/` holds configuration and database setup
- `app/services/` contains matching, ranking, assignment, marketplace, and collaboration logic
- `app/routers/` exposes REST endpoints
- `app/models/` and `app/schemas/` separate persisted data models from request/response DTOs
- `seed/` contains demo data for universities, solutions, and industry partners

## Prerequisites

Before running the app, make sure you have:

- Python 3.11 or later
- MongoDB running locally or a valid MongoDB Atlas connection string
- Git installed

## Setup

From the project root:

```bash
cd backend
python -m venv venv
```

On Windows:

```powershell
.\venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

Then install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file based on the example:

```bash
copy .env.example .env
```

Update the connection string in `.env` if needed:

```env
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?appName=SIH2026
MONGO_DB_NAME=university_matching
```

## Run the backend

Start the FastAPI server:

```bash
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Check the app:

- API docs: http://localhost:8000/docs
- Health endpoint: http://localhost:8000/api/health

On first startup, if the database is empty, demo data is automatically seeded.

## Run the test frontend

From the project root:

```bash
cd frontend-test
python -m http.server 5500
```

Then open:

```text
http://localhost:5500
```

The demo frontend communicates directly with the backend and supports:

- selecting or entering a sample problem
- running the matching engine
- reviewing the ranked assignment chain
- accepting or rejecting the current SENT assignment
- browsing marketplace solutions
- expressing interest and creating collaborations

## Running tests

From the backend directory:

```bash
pytest app/tests -q
```

The suite currently covers:

- scoring factors
- final weighted score calculation
- ranking and tie-break logic
- state machine transitions for assignments
- marketplace filtering
- industry interest and collaboration workflows

## Demo data

The project seeds demo data including:

- universities
- solutions
- industry partners
- sample problem data

This is useful for validating the matching pipeline without needing a live external system.

## Notes on integration

The categorization system is treated as an external black box. The project isolates that dependency in:

- `backend/app/integrations/categorization_adapter.py`

This keeps the rest of the service independent from the upstream JSON format.

## Authentication mode

The app supports a dev-only mode for local testing:

- `DEV_MODE=true`
- custom headers such as `X-Dev-User-Id` and `X-Dev-Role`

This is intended for the demo/test frontend and local development, not production.

## Current status

This repository includes the working backend logic and local demo tooling for a university matching + marketplace module. It is structured so the project can be evolved into a real platform without rewriting the core API contracts.

## License

This project is provided for internal project use and demonstration purposes.
