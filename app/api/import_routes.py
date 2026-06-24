from fastapi import APIRouter, Depends
from app.schemas.asset import AssetImport, AssetResponse
from app.services.importer import import_asset
from app.database.db import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/import", response_model= AssetResponse)
def import_assets(asset: AssetImport, db:Session=Depends(get_db)):
    results = import_asset(db, asset)
    return results