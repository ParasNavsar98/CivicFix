"""
Authentication and development header helper utilities.
Source: UniversityMatchingAlgo/backend/app/core/auth.py
"""
from typing import Optional
from fastapi import Header, HTTPException, status


def get_current_user_id(
    x_dev_user_id: Optional[str] = Header(None, alias="X-Dev-User-Id"),
    authorization: Optional[str] = Header(None),
) -> str:
    """Extract current user ID from dev headers or auth token."""
    if x_dev_user_id:
        return x_dev_user_id
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        return f"user_{token[:8]}"
    return "dev_user_default"
