from pydantic import BaseModel

class EnrichAsset(BaseModel):
    type: str
    value: str
    status: str
    source: str
    tags: list[str] = []
    metadata: dict = {}
