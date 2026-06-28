from fastapi import APIRouter
from app.agents.report_agent import ReportAgent 
from app.schemas.ask_request import AskRequest

router = APIRouter()
generator = ReportAgent()

@router.post("/report")
async def ask_ai(question : AskRequest):
    return generator.run(question)

