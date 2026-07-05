from fastapi import APIRouter

from app.ai.playbook_engine import generate_playbook
from app.ai.smart_money_engine import analyze_smart_money

router = APIRouter(prefix="/intelligence", tags=["Market Intelligence"])


@router.get("/smart-money/{symbol}")
def smart_money(symbol: str):
    return analyze_smart_money(symbol)


@router.get("/playbook/{symbol}")
def playbook(symbol: str):
    return generate_playbook(symbol)