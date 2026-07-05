from datetime import datetime

from app.ai.bot_engine import start_bot, stop_bot, list_bots, run_bot_cycle
from app.ai.quantum_pro_engine import (
    start_quantum_pro_bot,
    stop_quantum_pro_bot,
    list_quantum_pro_bots,
    run_quantum_pro_cycle,
)
from app.trading.trade_executor import get_trading_mode
from app.trading.gateio_client import get_best_bid_ask


manager_state = {
    "active": False,
    "initial_balance": 0,
    "cash_reserve": 0,
    "daily_target_percent": 15,
    "max_daily_loss_percent": 3,
    "started_at": None,
    "last_cycle_at": None,
    "normal_bot_ids": [],
    "pro_bot_ids": [],
    "events": [],
}


def now():
    return datetime.utcnow().isoformat()


def portfolio_manager_status():
    normal = list_bots()
    pro = list_quantum_pro_bots()

    total_pnl = 0

    for bot in normal.get("running", []):
        total_pnl += float(bot.get("total_pnl", 0) or 0)

    for bot in pro.get("running", []):
        total_pnl += float(bot.get("total_pnl", 0) or 0)

    initial = float(manager_state.get("initial_balance", 0) or 0)
    profit_percent = round((total_pnl / initial) * 100, 4) if initial > 0 else 0

    return {
        "mode": get_trading_mode(),
        "active": manager_state["active"],
        "initial_balance": manager_state["initial_balance"],
        "cash_reserve": manager_state["cash_reserve"],
        "daily_target_percent": manager_state["daily_target_percent"],
        "max_daily_loss_percent": manager_state["max_daily_loss_percent"],
        "total_pnl": round(total_pnl, 4),
        "profit_percent": profit_percent,
        "target_reached": profit_percent >= manager_state["daily_target_percent"],
        "started_at": manager_state["started_at"],
        "last_cycle_at": manager_state["last_cycle_at"],
        "normal_bot_ids": manager_state["normal_bot_ids"],
        "pro_bot_ids": manager_state["pro_bot_ids"],
        "events": manager_state["events"][-30:],
        "normal_bots": normal.get("running", []),
        "quantum_pro_bots": pro.get("running", []),
    }


def start_portfolio_manager(
    balance: float = 100,
    daily_target_percent: float = 15,
    max_daily_loss_percent: float = 3,
):
    mode = get_trading_mode()

    if mode == "LIVE":
        return {
            "error": "LIVE mod kapali. Once TESTNET/PAPER performans dogrulanmali.",
            "mode": mode,
        }

    balance = safe_balance(balance)
    daily_target_percent = safe_target(daily_target_percent)
    max_daily_loss_percent = safe_loss(max_daily_loss_percent)

    manager_state["active"] = True
    manager_state["initial_balance"] = balance
    manager_state["daily_target_percent"] = daily_target_percent
    manager_state["max_daily_loss_percent"] = max_daily_loss_percent
    manager_state["cash_reserve"] = round(balance * 0.20, 2)
    manager_state["started_at"] = now()
    manager_state["last_cycle_at"] = None
    manager_state["normal_bot_ids"] = []
    manager_state["pro_bot_ids"] = []
    manager_state["events"] = []

    allocations = build_allocations(balance)

    events = []

    for item in allocations:
        if item["type"] == "NORMAL":
            result = start_normal_managed_bot(item)
            events.append(result)

        if item["type"] == "PRO":
            result = start_pro_managed_bot(item)
            events.append(result)

    manager_state["events"].extend(events)

    return {
        "message": "Quantum Portfolio Manager started",
        "mode": mode,
        "balance": balance,
        "allocations": allocations,
        "events": events,
        "status": portfolio_manager_status(),
    }


def run_portfolio_manager_cycle():
    if not manager_state["active"]:
        return {"error": "Portfolio Manager aktif degil"}

    normal_cycle = run_bot_cycle()
    pro_cycle = run_quantum_pro_cycle()

    manager_state["last_cycle_at"] = now()

    status = portfolio_manager_status()

    total_pnl = status["total_pnl"]
    initial = manager_state["initial_balance"]
    max_loss = initial * manager_state["max_daily_loss_percent"] / 100

    events = [
        {
            "time": now(),
            "action": "CYCLE",
            "normal_actions": normal_cycle.get("actions", []),
            "pro_actions": pro_cycle.get("actions", []),
            "total_pnl": total_pnl,
            "profit_percent": status["profit_percent"],
        }
    ]

    if total_pnl <= -abs(max_loss):
        stop_all_managed_bots()
        manager_state["active"] = False
        events.append(
            {
                "time": now(),
                "action": "MANAGER_STOPPED_MAX_LOSS",
                "message": "Gunluk zarar limiti nedeniyle tum botlar durduruldu.",
            }
        )

    elif status["target_reached"]:
        events.append(
            {
                "time": now(),
                "action": "TARGET_REACHED",
                "message": "Gunluk hedef goruldu. Botlar yeni cycle icin calismaya devam edebilir.",
            }
        )

    manager_state["events"].extend(events)

    return {
        "message": "Portfolio Manager cycle completed",
        "events": events,
        "status": portfolio_manager_status(),
    }


def stop_portfolio_manager():
    stop_result = stop_all_managed_bots()

    manager_state["active"] = False
    manager_state["events"].append(
        {
            "time": now(),
            "action": "MANAGER_STOPPED",
        }
    )

    return {
        "message": "Portfolio Manager stopped",
        "stop_result": stop_result,
        "status": portfolio_manager_status(),
    }


def stop_all_managed_bots():
    stopped = []

    for bot_id in list(manager_state["normal_bot_ids"]):
        stopped.append(
            {
                "type": "NORMAL",
                "id": bot_id,
                "result": stop_bot(bot_id),
            }
        )

    for bot_id in list(manager_state["pro_bot_ids"]):
        stopped.append(
            {
                "type": "PRO",
                "id": bot_id,
                "result": stop_quantum_pro_bot(bot_id),
            }
        )

    return stopped


def build_allocations(balance):
    reserve = round(balance * 0.20, 2)
    active_balance = balance - reserve

    return [
        {
            "type": "PRO",
            "bot_id": "qe_spot_1",
            "amount": round(active_balance * 0.35, 2),
        },
        {
            "type": "PRO",
            "bot_id": "qe_spot_2",
            "amount": round(active_balance * 0.25, 2),
        },
        {
            "type": "NORMAL",
            "bot_id": "quantum_ai",
            "symbol": "BTCUSDT",
            "amount": round(active_balance * 0.20, 2),
            "tp_percent": 0.75,
            "sl_percent": 0.40,
        },
        {
            "type": "NORMAL",
            "bot_id": "momentum",
            "symbol": "BTCUSDT",
            "amount": round(active_balance * 0.20, 2),
            "tp_percent": 0.70,
            "sl_percent": 0.40,
        },
    ]


def start_normal_managed_bot(item):
    if not expected_profit_ok(item["symbol"], item["tp_percent"]):
        return {
            "type": "NORMAL",
            "bot_id": item["bot_id"],
            "status": "SKIPPED",
            "reason": "Spread/komisyon sonrasi beklenen kar yetersiz",
        }

    result = start_bot(
        bot_id=item["bot_id"],
        symbol=item["symbol"],
        amount_usd=item["amount"],
        daily_target_usd=max(1, round(item["amount"] * 0.15, 2)),
        daily_loss_limit_usd=max(0.5, round(item["amount"] * 0.03, 2)),
        auto_select=False,
        auto_reentry=False,
        max_daily_trades=10,
        tp_percent=item["tp_percent"],
        sl_percent=item["sl_percent"],
    )

    bot = result.get("bot")

    if bot:
        manager_state["normal_bot_ids"].append(bot["id"])

    return {
        "type": "NORMAL",
        "bot_id": item["bot_id"],
        "amount": item["amount"],
        "result": result,
    }


def start_pro_managed_bot(item):
    result = start_quantum_pro_bot(
        bot_id=item["bot_id"],
        balance=item["amount"],
        target_percent=5,
        max_loss_percent=3,
        compound=True,
    )

    bot = result.get("bot")

    if bot:
        manager_state["pro_bot_ids"].append(bot["id"])

    return {
        "type": "PRO",
        "bot_id": item["bot_id"],
        "amount": item["amount"],
        "result": result,
    }


def expected_profit_ok(symbol, tp_percent):
    book = get_best_bid_ask(symbol)

    if not book.get("ok"):
        return False

    spread_percent = float(book.get("spread_percent", 0) or 0)

    estimated_fee_percent = 0.20
    safety_buffer_percent = 0.10
    required_profit = spread_percent + estimated_fee_percent + safety_buffer_percent

    return float(tp_percent) > required_profit


def safe_balance(value):
    balance = float(value or 100)

    if balance < 30:
        balance = 30

    if balance > 1000:
        balance = 1000

    return balance


def safe_target(value):
    target = float(value or 15)

    if target < 1:
        target = 1

    if target > 15:
        target = 15

    return target


def safe_loss(value):
    loss = float(value or 3)

    if loss < 1:
        loss = 1

    if loss > 3:
        loss = 3

    return loss