from pydantic import BaseModel
from typing import List, Dict, Any
from app.database.models import AssetType, AssetStatus

class AssetImport(BaseModel):
    id: str
    type: AssetType
    value: str
    status: AssetStatus
    source: str
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class AssetResponse(BaseModel):
    id: str
    type: AssetType
    value: str
    status: AssetStatus
    source: str
    tags: List[str]
    metadata_json: Dict[str, Any]

    model_config = {
    "from_attributes": True
    }