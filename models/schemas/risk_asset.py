from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class AssetRisk(BaseModel):
    type: str
    status: Optional[str] = "active"
    tags: Optional[List[str]] = []
    metadata: Optional[Dict] = {}
    last_seen: Optional[datetime] = None