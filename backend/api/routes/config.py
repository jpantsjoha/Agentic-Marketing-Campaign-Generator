from fastapi import APIRouter
from pydantic import BaseModel
import os

from agents import marketing_orchestrator as orchestrator

router = APIRouter()

class GeminiKeyRequest(BaseModel):
    gemini_api_key: str

@router.post("/config/gemini-key")
async def set_gemini_key(req: GeminiKeyRequest):
    os.environ["GEMINI_API_KEY"] = req.gemini_api_key
    orchestrator.update_gemini_api_key(req.gemini_api_key)
    from ..main import reload_marketing_agent
    await reload_marketing_agent()
    return {"success": True}
