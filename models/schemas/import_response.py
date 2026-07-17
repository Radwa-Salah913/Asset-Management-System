from pydantic import BaseModel
from typing import Any

class ImportError(BaseModel):
    index: int
    asset: dict[str, Any]
    reason: Any


class ImportSummary(BaseModel):
    imported: int
    updated: int
    skipped: int
    total: int


class BatchImportResponse(BaseModel):
    summary: ImportSummary
    errors: list[ImportError]