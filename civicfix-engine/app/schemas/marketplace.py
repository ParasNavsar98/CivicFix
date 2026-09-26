"""
Pydantic Schemas for Industry Marketplace & Collaborations.
Source: UniversityMatchingAlgo/backend/app/schemas/
"""
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class DevelopmentStageEnum(str, Enum):
    CONCEPT = "CONCEPT"
    PROTOTYPE = "PROTOTYPE"
    PILOT = "PILOT"
    PRODUCTION_READY = "PRODUCTION_READY"


class SupportNeededEnum(str, Enum):
    FUNDING = "FUNDING"
    MENTORSHIP = "MENTORSHIP"
    PILOT_TESTING = "PILOT_TESTING"
    COMMERCIALIZATION = "COMMERCIALIZATION"


class SolutionResponse(BaseModel):
    solution_id: str
    university_id: str
    university_name: str
    title: str
    description: str
    domain: str
    subcategory: str
    development_stage: DevelopmentStageEnum
    support_needed: List[SupportNeededEnum]
    location: dict
    partner_type: str
    status: str
    visibility: str
    created_at: str


class ExpressInterestRequest(BaseModel):
    solution_id: str
    partner_id: str
    partner_name: str
    message: str
    contact_email: str


class ExpressInterestResponse(BaseModel):
    interest_id: str
    solution_id: str
    partner_id: str
    status: str
    created_at: str


class CreateCollaborationRequest(BaseModel):
    interest_id: str
    agreed_scope: str


class CollaborationResponse(BaseModel):
    collaboration_id: str
    interest_id: str
    solution_id: str
    university_id: str
    partner_id: str
    agreed_scope: str
    status: str
    created_at: str
