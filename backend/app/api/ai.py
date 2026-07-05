from fastapi import APIRouter

from app.ai.coins import TOP_AI_COINS
from app.ai.confidence_engine import calculate_ai_confidence

router = APIRouter(prefix="/ai", tags=["AI Engine"])


@router.get("/confidence")
def ai_confidence_all():
    return {
        symbol: calculate_ai_confidence(symbol)
        for symbol in TOP_AI_COINS
    }


@router.get("/confidence/top/{limit}")
def ai_confidence_top(limit: int):
    safe_limit = max(1, min(limit, len(TOP_AI_COINS)))

    return {
        symbol: calculate_ai_confidence(symbol)
        for symbol in TOP_AI_COINS[:safe_limit]
    }


@router.get("/confidence/{symbol}")
def ai_confidence_symbol(symbol: str):
    return calculate_ai_confidence(symbol.upper())