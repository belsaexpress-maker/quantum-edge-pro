from fastapi import APIRouter
from pydantic import BaseModel

from app.trading.gateio_client import (
    cancel_many_open_orders,
    cancel_open_orders,
    get_open_orders,
)
from app.trading.trade_executor import (
    execute_trade,
    get_trading_status,
    test_exchange_connection,
)

router = APIRouter(prefix="/trading", tags=["Trading"])


class TestOrderRequest(BaseModel):
    symbol: str = "BTCUSDT"
    side: str = "buy"
    price: float = 10000
    quantity: float = 0.0001


class CancelOrdersRequest(BaseModel):
    symbol: str = "BTCUSDT"


class CancelManyOrdersRequest(BaseModel):
    symbols: list[str] = [
        "BTCUSDT",
        "ETHUSDT",
        "XRPUSDT",
        "ADAUSDT",
        "WLDUSDT",
        "DOGE5SUSDT",
    ]


@router.get("/status")
def trading_status():
    return get_trading_status()


@router.get("/test")
def trading_test():
    return test_exchange_connection()


@router.get("/open-orders")
def trading_open_orders(symbol: str | None = None):
    return get_open_orders(symbol=symbol)


@router.post("/cancel-open-orders")
def trading_cancel_open_orders(payload: CancelOrdersRequest):
    return cancel_open_orders(symbol=payload.symbol)


@router.post("/cancel-many-open-orders")
def trading_cancel_many_open_orders(payload: CancelManyOrdersRequest):
    return cancel_many_open_orders(symbols=payload.symbols)


@router.post("/test-order")
def trading_test_order(payload: TestOrderRequest):
    return execute_trade(
        symbol=payload.symbol,
        side=payload.side,
        price=payload.price,
        quantity=payload.quantity,
    )