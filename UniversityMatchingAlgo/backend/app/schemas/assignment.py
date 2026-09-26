from pydantic import BaseModel


class RejectAssignmentRequest(BaseModel):
    reason: str
