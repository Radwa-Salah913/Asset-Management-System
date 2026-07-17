from fastapi import APIRouter, Depends
from app.schemas.import_response import BatchImportResponse
from app.services.importer import import_assets_batch
from app.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List, Dict, Any

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# I used List[Dict[str, Any]] instead of AssetImport --> bec. I will validate in service file to handle Malformed import.
@router.post("/import", response_model= BatchImportResponse)
async def import_assets(assets: List[Dict[str, Any]], db:Session=Depends(get_db)):
    results = import_assets_batch(db, assets)
    return results