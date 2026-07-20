from fastapi import APIRouter,Depends
from app.database.db import SessionLocal
from sqlalchemy.orm import Session
from app.database.models import Asset

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/get_assets")
async def get_assets(db:Session = Depends(get_db)):
    ans = await db.query(Asset).all()
    return ans
