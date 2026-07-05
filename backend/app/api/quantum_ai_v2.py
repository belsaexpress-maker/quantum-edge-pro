from fastapi import APIRouter
from pydantic import BaseModel

from app.ai.quantum_ai_engine_v2 import (
    portfolio_allocation_v2,
    record_trade_result,
    run_quantum_ai_v2_scan,
)

router = APIRouter(prefix="/quantum-ai-v2", tags=["Quantum AI Engine v2"])


class ScanRequest(BaseModel):
    limit: int = 50


class AllocationRequest(BaseModel):
    balance: float = 100


class TradeResultRequest(BaseModel):
    symbol: str
    bot_id: str
    pnl: float


@router.get("/scan")
def scan(limit: int = 50):
    return run_quantum_ai_v2_scan(limit=limit)


@router.post("/scan")
def post_scan(payload: ScanRequest):
    return run_quantum_ai_v2_scan(limit=payload.limit)


@router.post("/allocation")
def allocation(payload: AllocationRequest):
    return portfolio_allocation_v2(balance=payload.balance)


@router.post("/record-trade")
def record_trade(payload: TradeResultRequest):
    return record_trade_result(
        symbol=payload.symbol,
        bot_id=payload.bot_id,
        pnl=payload.pnl,
    )