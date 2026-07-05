from fastapi import APIRouter
from pydantic import BaseModel

from app.ai.portfolio_manager import (
    portfolio_manager_status,
    run_portfolio_manager_cycle,
    start_portfolio_manager,
    stop_portfolio_manager,
)

router = APIRouter(prefix="/portfolio-manager", tags=["Portfolio Manager"])


class StartPortfolioManagerRequest(BaseModel):
    balance: float = 100
    daily_target_percent: float = 15
    max_daily_loss_percent: float = 3


@router.get("/status")
def status():
    return portfolio_manager_status()


@router.post("/start")
def start(payload: StartPortfolioManagerRequest):
    return start_portfolio_manager(
        balance=payload.balance,
        daily_target_percent=payload.daily_target_percent,
        max_daily_loss_percent=payload.max_daily_loss_percent,
    )


@router.post("/cycle")
def cycle():
    return run_portfolio_manager_cycle()


@router.post("/stop")
def stop():
    return stop_portfolio_manager()