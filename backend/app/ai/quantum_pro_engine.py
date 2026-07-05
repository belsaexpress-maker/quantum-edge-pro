from datetime import datetime

from app.ai.opportunity_engine import scan_opportunities
from app.market_engine.market_manager import get_market_snapshot
from app.trading.trade_executor import execute_trade, get_trading_mode

pro_state = {"bots": []}

PRO_BOTS = [
    {"id": "qe_spot_1", "name": "QuantumEdge Pro Spot 1", "market": "SPOT", "risk": "Safe", "min_score": 90, "tp": 0.30, "sl": 0.80, "max_trades": 60, "trend_hold_score": 88},
    {"id": "qe_spot_2", "name": "QuantumEdge Pro Spot 2", "market": "SPOT", "risk": "Fast", "min_score": 75, "tp": 0.18, "sl": 0.60, "max_trades": 180, "trend_hold_score": 85},
    {"id": "qe_futures_1", "name": "QuantumEdge Pro Futures 1", "market": "FUTURES", "risk": "Balanced", "min_score": 85, "tp": 0.35, "sl": 0.80, "max_trades": 100, "trend_hold_score": 88},
    {"id": "qe_futures_2", "name": "QuantumEdge Pro Futures 2", "market": "FUTURES", "risk": "Aggressive", "min_score": 70, "tp": 0.20, "sl": 0.70, "max_trades": 220, "trend_hold_score": 82},
]


def now():
    return datetime.utcnow().isoformat()


def list_quantum_pro_bots():
    refresh_prices()
    return {"mode": get_trading_mode(), "templates": PRO_BOTS, "running": pro_state["bots"]}


def start_quantum_pro_bot(bot_id, balance=30, target_percent=15, max_loss_percent=3, compound=True):
    template = next((b for b in PRO_BOTS if b["id"] == bot_id), None)
    if not template:
        return {"error": "QuantumEdge Pro bot bulunamadı"}

    setup = select_setup(template)
    if not setup:
        return {"error": "Opportunity Engine uygun fırsat bulamadı"}

    price = get_price(setup["symbol"])
    if price <= 0:
        return {"error": "Canlı fiyat bulunamadı"}

    trade_amount = calculate_trade_amount(balance, setup["opportunity_score"])
    quantity = trade_amount / price

    order = execute_trade(setup["symbol"], "BUY", price, quantity)
    if order.get("error"):
        return order

    trend_hold = detect_trend_hold(template, setup)

    bot = {
        "id": len(pro_state["bots"]) + 1,
        "bot_id": bot_id,
        "name": template["name"],
        "market": template["market"],
        "risk": template["risk"],
        "symbol": setup["symbol"],
        "side": "LONG",
        "status": "RUNNING",
        "position_status": "OPEN",
        "cycle": 1,
        "portfolio_balance": round(balance, 2),
        "cycle_start_balance": round(balance, 2),
        "cycle_target_balance": round(balance * (1 + target_percent / 100), 2),
        "current_equity": round(balance, 2),
        "target_percent": target_percent,
        "max_loss_percent": max_loss_percent,
        "compound": compound,
        "entry_price": round(price, 8),
        "current_price": round(price, 8),
        "highest_price": round(price, 8),
        "quantity": round(quantity, 8),
        "trade_amount": round(trade_amount, 2),
        "tp_percent": template["tp"],
        "sl_percent": template["sl"],
        "trailing_stop_percent": 0.45,
        "trend_hold_mode": trend_hold["enabled"],
        "trend_hold_reason": trend_hold["reason"],
        "exit_mode": "SELL_SIGNAL" if trend_hold["enabled"] else "MICRO_TP",
        "max_trades": template["max_trades"],
        "trade_count": 1,
        "consecutive_losses": 0,
        "realized_pnl": 0,
        "unrealized_pnl": 0,
        "total_pnl": 0,
        "daily_profit_percent": 0,
        "ai_score": setup["ai_score"],
        "smart_money_score": setup["smart_money_score"],
        "opportunity_score": setup["opportunity_score"],
        "reasons": setup["reasons"],
        "last_action": "PRO_BUY_OPENED",
        "orders": [order_log("BUY", setup["symbol"], price, quantity, None, "PRO_START", setup, trend_hold["enabled"])],
        "created_at": now(),
        "updated_at": now(),
        "last_order_response": order,
    }

    pro_state["bots"].append(bot)
    return {"message": "QuantumEdge Pro bot started", "mode": get_trading_mode(), "bot": bot}


def stop_quantum_pro_bot(bot_id):
    refresh_prices()
    bot = next((b for b in pro_state["bots"] if b["id"] == bot_id), None)

    if not bot:
        return {"error": "Bot bulunamadı"}

    if bot["position_status"] == "OPEN":
        close_position(bot, "MANUAL_CLOSE")

    bot["status"] = "STOPPED"
    bot["position_status"] = "CLOSED"
    bot["last_action"] = "STOPPED"
    bot["updated_at"] = now()

    return {"message": "QuantumEdge Pro bot stopped", "bot": bot}


def run_quantum_pro_cycle():
    refresh_prices()
    actions = []

    for bot in pro_state["bots"]:
        if bot["status"] != "RUNNING":
            continue

        if bot["trade_count"] >= bot["max_trades"]:
            bot["status"] = "PAUSED"
            bot["last_action"] = "MAX_TRADES_REACHED"
            actions.append({"bot": bot["id"], "action": "PAUSED_MAX_TRADES"})
            continue

        if bot["consecutive_losses"] >= 3:
            bot["status"] = "LOCKED"
            bot["last_action"] = "LOCKED_3_LOSSES"
            actions.append({"bot": bot["id"], "action": "LOCKED_3_LOSSES"})
            continue

        loss_limit = bot["cycle_start_balance"] * bot["max_loss_percent"] / 100
        if bot["total_pnl"] <= -abs(loss_limit):
            bot["status"] = "LOCKED"
            bot["last_action"] = "MAX_DAILY_LOSS"
            actions.append({"bot": bot["id"], "action": "MAX_DAILY_LOSS"})
            continue

        target_profit = bot["cycle_start_balance"] * bot["target_percent"] / 100
        if bot["total_pnl"] >= target_profit:
            reset_cycle(bot)
            actions.append({"bot": bot["id"], "action": "TARGET_REACHED_NEW_CYCLE"})

        price_change = price_change_percent(bot)

        if bot["current_price"] > bot["highest_price"]:
            bot["highest_price"] = bot["current_price"]

        if bot["trend_hold_mode"]:
            exit_signal = detect_sell_signal(bot)
            if exit_signal["sell"]:
                close_position(bot, exit_signal["reason"])
                reopen_position(bot)
                actions.append({"bot": bot["id"], "action": exit_signal["reason"]})
            else:
                bot["last_action"] = "TREND_HOLD_WAIT_SELL_SIGNAL"
                actions.append({"bot": bot["id"], "action": "TREND_HOLD"})
        else:
            if price_change >= bot["tp_percent"]:
                close_position(bot, "MICRO_TAKE_PROFIT")
                reopen_position(bot)
                actions.append({"bot": bot["id"], "action": "MICRO_TP_REENTRY"})
            elif price_change <= -abs(bot["sl_percent"]):
                close_position(bot, "STOP_LOSS")
                reopen_position(bot)
                actions.append({"bot": bot["id"], "action": "SL_REENTRY"})
            else:
                upgrade = maybe_enable_trend_hold(bot)
                if upgrade["enabled"]:
                    bot["trend_hold_mode"] = True
                    bot["trend_hold_reason"] = upgrade["reason"]
                    bot["exit_mode"] = "SELL_SIGNAL"
                    bot["last_action"] = "UPGRADED_TO_TREND_HOLD"
                    actions.append({"bot": bot["id"], "action": "UPGRADED_TO_TREND_HOLD"})
                else:
                    bot["last_action"] = "HOLD"
                    actions.append({"bot": bot["id"], "action": "HOLD"})

        bot["updated_at"] = now()

    return {"message": "Quantum Pro cycle completed", "mode": get_trading_mode(), "actions": actions, "running": pro_state["bots"]}


def close_position(bot, reason):
    price = get_price(bot["symbol"]) or bot["current_price"]
    order = execute_trade(bot["symbol"], "SELL", price, bot["quantity"])

    if order.get("error"):
        bot["last_action"] = f"{reason}_FAILED"
        bot["last_order_response"] = order
        return order

    pnl = round((price - bot["entry_price"]) * bot["quantity"], 2)

    bot["realized_pnl"] = round(bot["realized_pnl"] + pnl, 2)
    bot["portfolio_balance"] = round(bot["portfolio_balance"] + pnl, 2)
    bot["current_equity"] = round(bot["portfolio_balance"], 2)
    bot["total_pnl"] = round(bot["realized_pnl"], 2)
    bot["unrealized_pnl"] = 0
    bot["daily_profit_percent"] = round(((bot["current_equity"] - bot["cycle_start_balance"]) / bot["cycle_start_balance"]) * 100, 2)
    bot["position_status"] = "CLOSED"
    bot["last_action"] = reason
    bot["last_order_response"] = order
    bot["orders"].append(order_log("SELL", bot["symbol"], price, bot["quantity"], pnl, reason, bot, bot["trend_hold_mode"]))

    bot["consecutive_losses"] = bot["consecutive_losses"] + 1 if pnl < 0 else 0
    return {"message": reason, "pnl": pnl, "order_response": order}


def reopen_position(bot):
    template = next((b for b in PRO_BOTS if b["id"] == bot["bot_id"]), None)
    setup = select_setup(template)

    if not setup:
        bot["last_action"] = "NO_OPPORTUNITY_SETUP"
        return {"error": "Opportunity Engine yeni setup bulamadı"}

    price = get_price(setup["symbol"])
    if price <= 0:
        return {"error": "Fiyat bulunamadı"}

    balance = bot["portfolio_balance"] if bot["compound"] else bot["cycle_start_balance"]
    amount = calculate_trade_amount(balance, setup["opportunity_score"])
    quantity = amount / price

    order = execute_trade(setup["symbol"], "BUY", price, quantity)
    if order.get("error"):
        bot["last_action"] = "REENTRY_FAILED"
        bot["last_order_response"] = order
        return order

    trend_hold = detect_trend_hold(template, setup)

    bot["symbol"] = setup["symbol"]
    bot["entry_price"] = round(price, 8)
    bot["current_price"] = round(price, 8)
    bot["highest_price"] = round(price, 8)
    bot["quantity"] = round(quantity, 8)
    bot["trade_amount"] = round(amount, 2)
    bot["position_status"] = "OPEN"
    bot["trade_count"] += 1
    bot["ai_score"] = setup["ai_score"]
    bot["smart_money_score"] = setup["smart_money_score"]
    bot["opportunity_score"] = setup["opportunity_score"]
    bot["reasons"] = setup["reasons"]
    bot["trend_hold_mode"] = trend_hold["enabled"]
    bot["trend_hold_reason"] = trend_hold["reason"]
    bot["exit_mode"] = "SELL_SIGNAL" if trend_hold["enabled"] else "MICRO_TP"
    bot["last_action"] = "REENTRY_OPENED"
    bot["last_order_response"] = order
    bot["orders"].append(order_log("BUY", setup["symbol"], price, quantity, None, "REENTRY", setup, trend_hold["enabled"]))

    return {"message": "Reentry opened", "order_response": order}


def select_setup(template):
    opportunities = scan_opportunities(200).get("items", [])
    active = {b["symbol"] for b in pro_state["bots"] if b.get("status") == "RUNNING" and b.get("position_status") == "OPEN"}

    for item in opportunities:
        symbol = item.get("symbol")
        score = item.get("opportunity_score", 0)
        decision = item.get("decision", "WAIT")

        if symbol in active:
            continue

        if score >= template["min_score"] and decision in ["STRONG_LONG", "LONG", "WATCH"]:
            return normalize_setup(item)

    fallback = next((x for x in opportunities if x.get("symbol") not in active), None)
    return normalize_setup(fallback) if fallback else None


def normalize_setup(item):
    return {
        "symbol": item.get("symbol"),
        "side": "LONG",
        "ai_score": item.get("ai_score", 0),
        "smart_money_score": item.get("smart_money_score", 0),
        "opportunity_score": item.get("opportunity_score", 0),
        "decision": item.get("decision", "WAIT"),
        "change_24h": item.get("change_24h", 0),
        "volume_24h": item.get("volume_24h", 0),
        "reasons": item.get("reasons", []),
        "raw": item,
    }


def detect_trend_hold(template, setup):
    score = setup.get("opportunity_score", 0)
    change = float(setup.get("change_24h", 0) or 0)
    volume = float(setup.get("volume_24h", 0) or 0)

    if score >= template.get("trend_hold_score", 88) and change > 1.2 and volume > 500_000:
        return {"enabled": True, "reason": "Strong uptrend detected by Opportunity Engine"}

    return {"enabled": False, "reason": "Micro TP mode: trend strength not enough"}


def maybe_enable_trend_hold(bot):
    opportunities = scan_opportunities(200).get("items", [])
    item = next((x for x in opportunities if x.get("symbol") == bot["symbol"]), None)

    if not item:
        return {"enabled": False, "reason": "No opportunity data"}

    if item.get("opportunity_score", 0) >= 88 and bot["unrealized_pnl"] > 0:
        return {"enabled": True, "reason": "Position upgraded by Opportunity Engine"}

    return {"enabled": False, "reason": "Trend hold not confirmed"}


def detect_sell_signal(bot):
    price_change = price_change_percent(bot)

    if price_change <= -abs(bot["sl_percent"]):
        return {"sell": True, "reason": "TREND_HOLD_STOP_LOSS"}

    trailing_stop_price = bot["highest_price"] * (1 - bot["trailing_stop_percent"] / 100)
    if bot["current_price"] <= trailing_stop_price and price_change > 0:
        return {"sell": True, "reason": "TRAILING_STOP_PROFIT_LOCK"}

    opportunities = scan_opportunities(200).get("items", [])
    item = next((x for x in opportunities if x.get("symbol") == bot["symbol"]), None)

    if item and item.get("opportunity_score", 0) < 60:
        return {"sell": True, "reason": "OPPORTUNITY_SCORE_WEAKENED"}

    return {"sell": False, "reason": "HOLD_TREND"}


def calculate_trade_amount(balance, score):
    if score >= 90:
        risk = 0.18
    elif score >= 75:
        risk = 0.12
    elif score >= 60:
        risk = 0.08
    else:
        risk = 0.05

    return max(5, round(balance * risk, 2))


def reset_cycle(bot):
    new_balance = bot["portfolio_balance"]
    bot["cycle"] += 1
    bot["cycle_start_balance"] = round(new_balance, 2)
    bot["cycle_target_balance"] = round(new_balance * (1 + bot["target_percent"] / 100), 2)
    bot["realized_pnl"] = 0
    bot["total_pnl"] = 0
    bot["daily_profit_percent"] = 0
    bot["last_action"] = "TARGET_REACHED_NEW_CYCLE"


def refresh_prices():
    for bot in pro_state["bots"]:
        if bot.get("position_status") != "OPEN":
            continue

        price = get_price(bot["symbol"])
        if price > 0:
            bot["current_price"] = round(price, 8)
            if price > bot.get("highest_price", 0):
                bot["highest_price"] = round(price, 8)

            bot["unrealized_pnl"] = round((price - bot["entry_price"]) * bot["quantity"], 2)
            bot["current_equity"] = round(bot["portfolio_balance"] + bot["unrealized_pnl"], 2)
            bot["total_pnl"] = round(bot["realized_pnl"] + bot["unrealized_pnl"], 2)
            bot["daily_profit_percent"] = round(((bot["current_equity"] - bot["cycle_start_balance"]) / bot["cycle_start_balance"]) * 100, 2)
            bot["price_change_percent"] = round(price_change_percent(bot), 3)
            bot["updated_at"] = now()


def price_change_percent(bot):
    if bot["entry_price"] <= 0:
        return 0
    return ((bot["current_price"] - bot["entry_price"]) / bot["entry_price"]) * 100


def get_price(symbol):
    snapshot = get_market_snapshot()
    item = next((c for c in snapshot.get("crypto", []) if c.get("symbol") == symbol.upper()), None)
    if not item:
        return 0
    return float(item.get("price", 0) or 0)


def order_log(side, symbol, price, quantity, pnl, reason, source, trend_hold):
    return {
        "side": side,
        "symbol": symbol,
        "price": round(price, 8),
        "quantity": round(quantity, 8),
        "value": round(price * quantity, 2),
        "pnl": pnl,
        "mode": get_trading_mode(),
        "ai_score": source.get("ai_score", source.get("ai_score", 0)),
        "smart_money_score": source.get("smart_money_score", 0),
        "opportunity_score": source.get("opportunity_score", 0),
        "trend_hold": trend_hold,
        "created_at": now(),
        "reason": reason,
    }