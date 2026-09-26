from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.config.database import ensure_indexes, get_db
from app.routers import universities, matching, assignments, marketplace, interests, collaborations

app = FastAPI(
    title="University Matching + Industry Marketplace Module",
    description=(
        "SIH project module: university capability matching, sequential "
        "assignment, and industry marketplace/collaboration. Consumes the "
        "categorization system's output as a black box."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(universities.router)
app.include_router(matching.router)
app.include_router(assignments.router)
app.include_router(marketplace.router)
app.include_router(interests.router)
app.include_router(collaborations.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def on_startup():
    ensure_indexes()
    if settings.seed_on_startup:
        db = get_db()
        if db.universities.count_documents({}) == 0:
            from seed.seed_db import run_seed  # local import to avoid hard dependency at import time

            run_seed(db)
