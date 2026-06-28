from pydantic import BaseModel
from typing import List


class RiskResponse(BaseModel):
    risk_score: int
    risk_level: str
    reasons: List[str]
    summary: str