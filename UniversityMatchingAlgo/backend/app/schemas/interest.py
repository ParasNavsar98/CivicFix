from pydantic import BaseModel


class ExpressInterestRequest(BaseModel):
    partnerId: str
    supportOffered: list[str] = []
    contribution: dict = {}
    message: str = ""


class RejectInterestRequest(BaseModel):
    reason: str
