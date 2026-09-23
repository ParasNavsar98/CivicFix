# api package
from app.api.problems import router as problems_router
from app.api.reviewer import router as reviewer_router
from app.api.routing import router as routing_router
from app.api.health import router as health_router

__all__ = [
    "problems_router",
    "reviewer_router",
    "routing_router",
    "health_router",
]
