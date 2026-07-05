from fastapi import APIRouter
from pydantic import BaseModel

from app.trading.trade_executor import (
    execute_trade,
    get_trading_status,
    test_exchange_connection,
)

router = APIRouter(prefix="/trading", tags=["Trading"])


class TradeRequest(BaseModel):
    symbol: str
    side: str
    price: float
    quantity: float


@router.get("/status")
def status():
    return get_trading_status()


@router.get("/test-connection")
def test_connection():
    return test_exchange_connection()


@router.post("/execute")
def execute(payload: TradeRequest):
    return execute_trade(
        symbol=payload.symbol,
        side=payload.side,
        price=payload.price,
        quantity=payload.quantity,
    )