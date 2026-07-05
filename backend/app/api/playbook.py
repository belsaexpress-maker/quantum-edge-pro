from fastapi import APIRouter

from app.ai.playbook_engine import generate_ai_playbook

router = APIRouter(prefix="/playbook", tags=["AI Playbook"])


@router.get("/{symbol}")
def get_playbook(symbol: str, timeframe: str = "1h"):
    return generate_ai_playbook(symbol.upper(), timeframe)