from fastapi import APIRouter
from pydantic import BaseModel

from app.ai.paper_trading_engine import (
    create_paper_order,
    get_paper_account,
    reset_paper_account,
)

router = APIRouter(prefix="/paper", tags=["Paper Trading"])


class PaperOrderRequest(BaseModel):
    symbol: str
    side: str
    price: float
    quantity: float


@router.get("/account")
def account():
    return get_paper_account()


@router.post("/order")
def order(payload: PaperOrderRequest):
    return create_paper_order(
        payload.symbol,
        payload.side,
        payload.price,
        payload.quantity,
    )


@router.post("/reset")
def reset():
    return reset_paper_account()