from fastapi import APIRouter
from pydantic import BaseModel

from app.ai.quantum_pro_engine import (
    list_quantum_pro_bots,
    run_quantum_pro_cycle,
    start_quantum_pro_bot,
    stop_quantum_pro_bot,
)

router = APIRouter(prefix="/quantum-pro-bots", tags=["QuantumEdge Pro Bots"])


class StartQuantumProRequest(BaseModel):
    bot_id: str
    balance: float = 30
    target_percent: float = 15
    max_loss_percent: float = 3
    compound: bool = True


@router.get("/")
def list_bots():
    return list_quantum_pro_bots()


@router.post("/start")
def start(payload: StartQuantumProRequest):
    return start_quantum_pro_bot(
        bot_id=payload.bot_id,
        balance=payload.balance,
        target_percent=payload.target_percent,
        max_loss_percent=payload.max_loss_percent,
        compound=payload.compound,
    )


@router.post("/stop/{bot_id}")
def stop(bot_id: int):
    return stop_quantum_pro_bot(bot_id)


@router.post("/cycle")
def cycle():
    return run_quantum_pro_cycle()