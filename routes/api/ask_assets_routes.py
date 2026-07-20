from fastapi import APIRouter
from app.services.asset_returner import AssetsReturner
from app.schemas.ask_request import AskRequest

router = APIRouter()
generator = AssetsReturner()

@router.post("/ask")
async def ask_ai(question : AskRequest):
    ans = await generator.run_query(question)
    return ans

