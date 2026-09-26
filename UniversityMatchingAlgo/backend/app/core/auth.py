"""
Auth boundary.

We do NOT build a second auth system. This decodes whatever JWT the main
platform's auth issues (shared secret assumed for now — swap for JWKS/OIDC
if the real system uses asymmetric keys, only this file changes).

DEV_MODE: while the real platform's auth isn't wired up yet, identity can be
passed via X-Dev-User-Id / X-Dev-Role headers. Logged clearly; must be
disabled (DEV_MODE=false) before anything resembling production use.
"""
import jwt
from fastapi import Header, HTTPException

from app.config.settings import settings


class CurrentUser:
    def __init__(self, user_id: str, role: str, university_id: str | None = None):
        self.user_id = user_id
        self.role = role
        self.university_id = university_id


def get_current_user(
    authorization: str | None = Header(default=None),
    x_dev_user_id: str | None = Header(default=None),
    x_dev_role: str | None = Header(default=None),
    x_dev_university_id: str | None = Header(default=None),
) -> CurrentUser:
    if settings.dev_mode and x_dev_user_id:
        return CurrentUser(
            user_id=x_dev_user_id,
            role=x_dev_role or "ADMIN",
            university_id=x_dev_university_id,
        )

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token.")

    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}")

    return CurrentUser(
        user_id=payload.get("sub", ""),
        role=payload.get("role", ""),
        university_id=payload.get("universityId"),
    )
