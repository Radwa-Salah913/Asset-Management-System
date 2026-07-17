from pydantic import BaseModel

class EnrichmentOutput(BaseModel):
    environment: str
    category: str
    criticality: str
    tags: list[str]
    description: str