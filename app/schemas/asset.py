from pydantic import BaseModel
from typing import List, Dict, Any
from app.database.models import AssetType, AssetStatus, AssetSource
from datetime import datetime
from uuid import UUID

class AssetImport(BaseModel):
    
    type: AssetType
    value: str
    status: AssetStatus
    source: AssetSource
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class AssetResponse(BaseModel):
    id: UUID
    type: AssetType
    value: str
    first_seen: datetime
    last_seen: datetime
    status: AssetStatus
    source: AssetSource
    tags: List[str]
    metadata_json: Dict[str, Any]

    model_config = {
    "from_attributes": True
    }