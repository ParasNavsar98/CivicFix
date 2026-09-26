"""
Shape of a `university_assignments` document (see plan doc for full field list).
Statuses: PENDING -> SENT -> ACCEPTED | REJECTED | TIMED_OUT | CANCELLED
"""

VALID_STATUSES = {"PENDING", "SENT", "ACCEPTED", "REJECTED", "TIMED_OUT", "CANCELLED"}
ACTIVE_STATUSES = {"PENDING", "SENT"}
