from datetime import datetime, timedelta

from app.ai.bot_strategy_engine import (
    build_grid_levels,
    can_reenter,
    get_bot_templates,
    should_open_position,
)
from app.ai.scanner_engine import get_scanner_results, scan_all_market
from app.market_engine.market_manager import get_market_snapshot
from app.trading.trade_executor import execute_trade, get_trading_mode


bot_state = {"bots": []}


def now_iso():
    return datetime.utcnow().isoformat()


def now_dt():
    return datetime.utcnow()


def list_bots():
    refresh_bot_prices()
    return {
        "mode": get_trading_mode(),
        "templates": get_bot_templates(),
        "running": bot_state["bots"],
    }


def start_bot(
    bot_id,
    symbol,
    amount_usd,
    daily_target_usd=10,
    daily_loss_limit_usd=5,
    auto_select=True,
    auto_reentry=True,
    max_daily_trades=100,
    tp_percent=0.25,
    sl_percent=0.7,
):
    template = next((b for b in get_bot_templates() if b["id"] == bot_id), None)

    if not template:
        return {"error": "Bot bulunamadı"}

    selected_symbol = select_best_symbol(symbol, auto_select, template["strategy"])
    price = find_price(selected_symbol)

    if price <= 0:
        return {"error": "Canlı fiyat bulunamadı"}

    quantity = amount_usd / price
    order_result = execute_trade(selected_symbol, "BUY", price, quantity)

    if order_result.get("error"):
        return order_result

    grid_levels = []
    if template["strategy"] == "GRID":
        grid_levels = build_grid_levels(
            price,
            template.get("grid_levels", 12),
            template.get("grid_range_percent", 2.0),
        )

    bot = {
        "id": len(bot_state["bots"]) + 1,
        "bot_id": bot_id,
        "name": template["name"],
        "strategy": template["strategy"],
        "symbol": selected_symbol,
        "amount_usd": round(amount_usd, 2),
        "daily_target_usd": round(daily_target_usd, 2),
        "daily_loss_limit_usd": round(daily_loss_limit_usd, 2),
        "max_daily_trades": int(max_daily_trades),
        "tp_percent": float(tp_percent),
        "sl_percent": float(sl_percent),
        "min_interval_seconds": template.get("min_interval_seconds", 10),
        "next_allowed_trade_at": (now_dt() + timedelta(seconds=template.get("min_interval_seconds", 10))).isoformat(),
        "dca_step_percent": template.get("dca_step_percent", 0.5),
        "max_dca_orders": template.get("max_dca_orders", 0),
        "dca_count": 0,
        "grid_levels": grid_levels,
        "grid_completed": 0,
        "entry_price": round(price, 8),
        "current_price": round(price, 8),
        "quantity": round(quantity, 8),
        "status": "RUNNING",
        "position_status": "OPEN",
        "risk": template["risk"],
        "unrealized_pnl": 0,
        "realized_pnl": 0,
        "total_pnl": 0,
        "trade_count": 1,
        "cycle_count": 0,
        "price_change_percent": 0,
        "auto_select": auto_select,
        "auto_reentry": auto_reentry,
        "trading_mode": get_trading_mode(),
        "last_action": "BUY_OPENED",
        "last_order_response": order_result,
        "orders": [
            make_order_log("BUY", selected_symbol, price, quantity, None, "BOT_START")
        ],
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }

    bot_state["bots"].append(bot)

    return {
        "message": "Bot started",
        "mode": get_trading_mode(),
        "bot": bot,
        "order_response": order_result,
    }


def stop_bot(bot_instance_id):
    refresh_bot_prices()
    bot = next((b for b in bot_state["bots"] if b["id"] == bot_instance_id), None)

    if not bot:
        return {"error": "Çalışan bot bulunamadı"}

    if bot["position_status"] == "OPEN":
        close_position(bot, "MANUAL_STOP")

    bot["status"] = "STOPPED"
    bot["position_status"] = "CLOSED"
    bot["last_action"] = "BOT_STOPPED"
    bot["stopped_at"] = now_iso()
    bot["updated_at"] = now_iso()

    return {"message": "Bot stopped", "mode": get_trading_mode(), "bot": bot}


def run_bot_cycle():
    refresh_bot_prices()
    actions = []

    for bot in bot_state["bots"]:
        if bot["status"] != "RUNNING":
            continue

        bot["cycle_count"] += 1

        if not interval_allowed(bot):
            bot["last_action"] = "WAIT_INTERVAL"
            actions.append({"bot_id": bot["id"], "action": "WAIT_INTERVAL"})
            continue

        if bot["trade_count"] >= bot["max_daily_trades"]:
            bot["status"] = "PAUSED"
            bot["last_action"] = "MAX_DAILY_TRADES_REACHED"
            actions.append({"bot_id": bot["id"], "action": "PAUSED_MAX_TRADES"})
            continue

        if bot["realized_pnl"] >= bot["daily_target_usd"]:
            bot["status"] = "PAUSED"
            bot["last_action"] = "DAILY_TARGET_REACHED"
            actions.append({"bot_id": bot["id"], "action": "PAUSED_TARGET_REACHED"})
            continue

        if bot["realized_pnl"] <= -abs(bot["daily_loss_limit_usd"]):
            bot["status"] = "PAUSED"
            bot["last_action"] = "DAILY_LOSS_LIMIT_REACHED"
            actions.append({"bot_id": bot["id"], "action": "PAUSED_LOSS_LIMIT"})
            continue

        if bot["position_status"] == "OPEN":
            price_change_percent = calculate_price_change_percent(bot)

            if bot["strategy"] == "DCA" and should_dca(bot, price_change_percent):
                actions.append({"bot_id": bot["id"], "action": "DCA_BUY", "result": add_dca_order(bot)})
                continue

            if bot["strategy"] == "GRID":
                update_grid_progress(bot)

            if price_change_percent >= bot["tp_percent"]:
                close_result = close_position(bot, "TAKE_PROFIT")
                actions.append({"bot_id": bot["id"], "action": "TAKE_PROFIT", "result": close_result})

                if bot["auto_reentry"]:
                    actions.append({"bot_id": bot["id"], "action": "REENTRY", "result": reopen_position(bot)})

            elif price_change_percent <= -abs(bot["sl_percent"]):
                close_result = close_position(bot, "STOP_LOSS")
                actions.append({"bot_id": bot["id"], "action": "STOP_LOSS", "result": close_result})

                if bot["auto_reentry"]:
                    actions.append({"bot_id": bot["id"], "action": "REENTRY_AFTER_LOSS", "result": reopen_position(bot)})
                else:
                    bot["status"] = "PAUSED"
                    bot["last_action"] = "PAUSED_AFTER_LOSS"

            else:
                bot["last_action"] = "HOLD"
                actions.append({"bot_id": bot["id"], "action": "HOLD"})

        elif bot["position_status"] == "CLOSED" and bot["auto_reentry"]:
            actions.append({"bot_id": bot["id"], "action": "REENTRY_FROM_CLOSED", "result": reopen_position(bot)})

        bot["updated_at"] = now_iso()

    return {
        "message": "Bot cycle completed",
        "mode": get_trading_mode(),
        "actions": actions,
        "bots": bot_state["bots"],
    }


def close_position(bot, reason):
    price = find_price(bot["symbol"]) or bot["current_price"] or bot["entry_price"]
    order_result = execute_trade(bot["symbol"], "SELL", price, bot["quantity"])

    if order_result.get("error"):
        bot["last_action"] = f"{reason}_FAILED"
        bot["last_order_response"] = order_result
        return order_result

    pnl = round((price - bot["entry_price"]) * bot["quantity"], 2)

    bot["realized_pnl"] = round(bot["realized_pnl"] + pnl, 2)
    bot["total_pnl"] = round(bot["realized_pnl"], 2)
    bot["unrealized_pnl"] = 0
    bot["exit_price"] = round(price, 8)
    bot["position_status"] = "CLOSED"
    bot["last_action"] = reason
    bot["last_order_response"] = order_result
    bot["orders"].append(make_order_log("SELL", bot["symbol"], price, bot["quantity"], pnl, reason))
    set_next_interval(bot)

    return {"message": reason, "pnl": pnl, "order_response": order_result}


def reopen_position(bot):
    if bot["trade_count"] >= bot["max_daily_trades"]:
        bot["status"] = "PAUSED"
        bot["last_action"] = "MAX_DAILY_TRADES_REACHED"
        return {"error": "Günlük işlem limiti doldu"}

    selected_symbol = select_best_symbol(bot["symbol"], bot["auto_select"], bot["strategy"])
    price = find_price(selected_symbol)

    if price <= 0:
        bot["last_action"] = "REENTRY_FAILED_NO_PRICE"
        return {"error": "Yeni pozisyon için fiyat bulunamadı"}

    quantity = bot["amount_usd"] / price
    order_result = execute_trade(selected_symbol, "BUY", price, quantity)

    if order_result.get("error"):
        bot["last_action"] = "REENTRY_FAILED_ORDER"
        bot["last_order_response"] = order_result
        return order_result

    bot["symbol"] = selected_symbol
    bot["entry_price"] = round(price, 8)
    bot["current_price"] = round(price, 8)
    bot["quantity"] = round(quantity, 8)
    bot["position_status"] = "OPEN"
    bot["trade_count"] += 1
    bot["dca_count"] = 0
    bot["unrealized_pnl"] = 0
    bot["price_change_percent"] = 0

    if bot["strategy"] == "GRID":
        bot["grid_levels"] = build_grid_levels(price, 12, 2.0)
        bot["grid_completed"] = 0

    bot["last_action"] = "REENTRY_BUY_OPENED"
    bot["last_order_response"] = order_result
    bot["orders"].append(make_order_log("BUY", selected_symbol, price, quantity, None, "REENTRY"))
    set_next_interval(bot)

    return {"message": "New position opened", "symbol": selected_symbol, "order_response": order_result}


def add_dca_order(bot):
    price = find_price(bot["symbol"])

    if price <= 0:
        return {"error": "DCA için fiyat bulunamadı"}

    quantity = bot["amount_usd"] / price
    order_result = execute_trade(bot["symbol"], "BUY", price, quantity)

    if order_result.get("error"):
        bot["last_action"] = "DCA_FAILED"
        bot["last_order_response"] = order_result
        return order_result

    old_value = bot["entry_price"] * bot["quantity"]
    new_value = price * quantity
    new_quantity = bot["quantity"] + quantity

    bot["entry_price"] = round((old_value + new_value) / new_quantity, 8)
    bot["quantity"] = round(new_quantity, 8)
    bot["current_price"] = round(price, 8)
    bot["dca_count"] += 1
    bot["trade_count"] += 1
    bot["last_action"] = "DCA_BUY"
    bot["last_order_response"] = order_result
    bot["orders"].append(make_order_log("BUY", bot["symbol"], price, quantity, None, "DCA"))
    set_next_interval(bot)

    return {"message": "DCA order opened", "order_response": order_result}


def refresh_bot_prices():
    for bot in bot_state["bots"]:
        if bot.get("position_status") != "OPEN":
            continue

        price = find_price(bot["symbol"])

        if price > 0:
            bot["current_price"] = round(price, 8)
            bot["unrealized_pnl"] = round((price - bot["entry_price"]) * bot["quantity"], 2)
            bot["total_pnl"] = round(bot["realized_pnl"] + bot["unrealized_pnl"], 2)
            bot["price_change_percent"] = round(calculate_price_change_percent(bot), 3)
            bot["updated_at"] = now_iso()

    return bot_state["bots"]


def update_grid_progress(bot):
    levels = bot.get("grid_levels", [])
    current = bot.get("current_price", 0)
    entry = bot.get("entry_price", 0)

    if not levels or current <= entry:
        return

    completed = len([level for level in levels if entry < level <= current])
    bot["grid_completed"] = completed


def should_dca(bot, price_change_percent):
    if bot["dca_count"] >= bot["max_dca_orders"]:
        return False

    trigger = -abs(bot["dca_step_percent"]) * (bot["dca_count"] + 1)
    return price_change_percent <= trigger


def calculate_price_change_percent(bot):
    if bot["entry_price"] <= 0:
        return 0

    return ((bot["current_price"] - bot["entry_price"]) / bot["entry_price"]) * 100


def interval_allowed(bot):
    value = bot.get("next_allowed_trade_at")

    if not value:
        return True

    try:
        return now_dt() >= datetime.fromisoformat(value)
    except Exception:
        return True


def set_next_interval(bot):
    seconds = int(bot.get("min_interval_seconds", 10))
    bot["next_allowed_trade_at"] = (now_dt() + timedelta(seconds=seconds)).isoformat()


def select_best_symbol(symbol, auto_select, strategy):
    if not auto_select and symbol != "AUTO":
        return symbol.upper()

    scan_all_market()
    best_items = get_scanner_results(200)["items"]

    active_symbols = {
        bot["symbol"]
        for bot in bot_state["bots"]
        if bot.get("status") == "RUNNING" and bot.get("position_status") == "OPEN"
    }

    candidates = [
        item
        for item in best_items
        if item.get("symbol") not in active_symbols and can_reenter(strategy, item, symbol)
    ]

    if candidates:
        return candidates[0]["symbol"]

    fallback = [item for item in best_items if item.get("symbol") not in active_symbols]

    if fallback:
        return fallback[0]["symbol"]

    if best_items:
        return best_items[0]["symbol"]

    return "BTCUSDT"


def find_price(symbol):
    snapshot = get_market_snapshot()
    coins = snapshot.get("crypto", [])

    item = next((coin for coin in coins if coin.get("symbol") == symbol.upper()), None)

    if not item:
        return 0

    return float(item.get("price", 0) or 0)


def make_order_log(side, symbol, price, quantity, pnl, reason):
    return {
        "side": side,
        "symbol": symbol,
        "price": round(price, 8),
        "quantity": round(quantity, 8),
        "value": round(price * quantity, 2),
        "pnl": pnl,
        "mode": get_trading_mode(),
        "created_at": now_iso(),
        "reason": reason,
    }