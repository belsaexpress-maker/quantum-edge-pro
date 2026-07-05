from fastapi import APIRouter
from pydantic import BaseModel

from app.ai.bot_engine import list_bots, run_bot_cycle, start_bot, stop_bot

router = APIRouter(prefix="/bots", tags=["Bots"])


class StartBotRequest(BaseModel):
    bot_id: str
    symbol: str = "AUTO"
    amount_usd: float = 100
    daily_target_usd: float = 10
    daily_loss_limit_usd: float = 5
    auto_select: bool = True
    auto_reentry: bool = True
    max_daily_trades: int = 100
    tp_percent: float = 0.25
    sl_percent: float = 0.7


@router.get("/")
def get_bots():
    return list_bots()


@router.post("/start")
def start(payload: StartBotRequest):
    return start_bot(
        bot_id=payload.bot_id,
        symbol=payload.symbol,
        amount_usd=payload.amount_usd,
        daily_target_usd=payload.daily_target_usd,
        daily_loss_limit_usd=payload.daily_loss_limit_usd,
        auto_select=payload.auto_select,
        auto_reentry=payload.auto_reentry,
        max_daily_trades=payload.max_daily_trades,
        tp_percent=payload.tp_percent,
        sl_percent=payload.sl_percent,
    )


@router.post("/stop/{bot_instance_id}")
def stop(bot_instance_id: int):
    return stop_bot(bot_instance_id)


@router.post("/cycle")
def cycle():
    return run_bot_cycle()