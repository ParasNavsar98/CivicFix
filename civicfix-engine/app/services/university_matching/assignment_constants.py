"""
Assignment status constants.
Source: UniversityMatchingAlgo/backend/app/models/assignment.py
Statuses: PENDING -> SENT -> ACCEPTED | REJECTED | TIMED_OUT | CANCELLED
"""

VALID_STATUSES = {"PENDING", "SENT", "ACCEPTED", "REJECTED", "TIMED_OUT", "CANCELLED"}
ACTIVE_STATUSES = {"PENDING", "SENT"}
