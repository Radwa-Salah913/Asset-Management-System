from pydantic import BaseModel,Field
from typing import List, Dict, Any
from app.database.models import AssetType, AssetStatus, AssetSource
from datetime import datetime
from uuid import UUID

class AssetImport(BaseModel):
    
    type: AssetType
    value: str = Field(..., min_length=1)
    status: AssetStatus
    source: AssetSource
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class AssetResponse(BaseModel):
    id: UUID
    type: AssetType
    value: str = Field(..., min_length=1)
    first_seen: datetime
    last_seen: datetime
    status: AssetStatus
    source: AssetSource
    tags: List[str]
    metadata_json: Dict[str, Any]

    model_config = {
    "from_attributes": True
    }