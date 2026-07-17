from fastapi import APIRouter
from app.services.asset_returner import AssetsReturner
from app.schemas.ask_request import AskRequest

router = APIRouter()
generator = AssetsReturner()

@router.post("/ask")
async def ask_ai(question : AskRequest):
    return generator.run_query(question)

