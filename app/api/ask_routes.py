from fastapi import APIRouter
from app.services.NL_asset_query import sqlGenerator 
from app.schemas.question import AskRequest
router = APIRouter()
generator = sqlGenerator()

@router.post("/ask")
async def ask_ai(question : AskRequest):
    return generator.run_query(question)

