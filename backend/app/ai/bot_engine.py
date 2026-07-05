from datetime import datetime, timedelta

from app.ai.bot_strategy_engine import (
    build_grid_levels,
    can_reenter,
    get_bot_templates,
)
from app.ai.scanner_engine import get_scanner_results, scan_all_market
from app.market_engine.market_manager import get_market_snapshot
from app.trading.trade_executor import execute_trade, get_trading_mode


bot_state = {"bots": []}


SAFE_MAX_DAILY_TRADES = 20
SAFE_MIN_INTERVAL_SECONDS = 60
SAFE_DEFAULT_TP_PERCENT = 0.60
SAFE_DEFAULT_SL_PERCENT = 0.35
SAFE_MAX_AMOUNT_USD = 30


BLOCKED_SYMBOL_PARTS = [
    "3L",
    "3S",
    "5L",
    "5S",
    "BULL",
    "BEAR",
    "UPUSDT",
    "DOWNUSDT",
]


def now_iso():
    return datetime.utcnow().isoformat()


def now_dt():
    return datetime.utcnow()


def list_bots():
    refresh_bot_prices()

    return {
        "mode": get_trading_mode(),
        "safety": {
            "live_enabled": False,
            "max_daily_trades": SAFE_MAX_DAILY_TRADES,
            "min_interval_seconds": SAFE_MIN_INTERVAL_SECONDS,
            "max_amount_usd": SAFE_MAX_AMOUNT_USD,
            "blocked_leveraged_tokens": BLOCKED_SYMBOL_PARTS,
        },
        "templates": get_bot_templates(),
        "running": bot_state["bots"],
    }


def start_bot(
    bot_id,
    symbol,
    amount_usd,
    daily_target_usd=10,
    daily_loss_limit_usd=3,
    auto_select=True,
    auto_reentry=False,
    max_daily_trades=20,
    tp_percent=SAFE_DEFAULT_TP_PERCENT,
    sl_percent=SAFE_DEFAULT_SL_PERCENT,
):
    template = next((b for b in get_bot_templates() if b["id"] == bot_id), None)

    if not template:
        return {"error": "Bot bulunamadı"}

    amount_usd = safe_amount(amount_usd)
    daily_loss_limit_usd = safe_daily_loss_limit(daily_loss_limit_usd)
    max_daily_trades = safe_max_daily_trades(max_daily_trades)
    tp_percent = safe_tp(tp_percent)
    sl_percent = safe_sl(sl_percent)

    selected_symbol = select_best_symbol(symbol, auto_select, template["strategy"])

    if not is_safe_symbol(selected_symbol):
        return {
            "error": "Riskli / kaldıraçlı token engellendi",
            "symbol": selected_symbol,
        }

    price = find_price(selected_symbol)

    if price <= 0:
        return {"error": "Canlı fiyat bulunamadı", "symbol": selected_symbol}

    quantity = calculate_quantity(amount_usd, price)

    if quantity <= 0:
        return {"error": "Miktar hesaplanamadı"}

    order_result = execute_trade(selected_symbol, "BUY", price, quantity)

    if not order_is_ok(order_result):
        return {
            "error": "BUY emri başarısız veya dolmadı. Bot pozisyon açmadı.",
            "symbol": selected_symbol,
            "order_response": order_result,
        }

    filled_amount = get_filled_amount(order_result) or quantity
    fill_price = get_fill_price(order_result) or price

    grid_levels = []

    if template["strategy"] == "GRID":
        grid_levels = build_grid_levels(
            fill_price,
            template.get("grid_levels", 8),
            template.get("grid_range_percent", 1.5),
        )

    bot = {
        "id": len(bot_state["bots"]) + 1,
        "bot_id": bot_id,
        "name": template["name"],
        "strategy": template["strategy"],
        "symbol": selected_symbol,
        "amount_usd": round(amount_usd, 2),
        "daily_target_usd": round(float(daily_target_usd), 2),
        "daily_loss_limit_usd": round(float(daily_loss_limit_usd), 2),
        "max_daily_trades": int(max_daily_trades),
        "tp_percent": float(tp_percent),
        "sl_percent": float(sl_percent),
        "min_interval_seconds": max(
            SAFE_MIN_INTERVAL_SECONDS,
            int(template.get("min_interval_seconds", SAFE_MIN_INTERVAL_SECONDS)),
        ),
        "next_allowed_trade_at": (
            now_dt()
            + timedelta(
                seconds=max(
                    SAFE_MIN_INTERVAL_SECONDS,
                    int(template.get("min_interval_seconds", SAFE_MIN_INTERVAL_SECONDS)),
                )
            )
        ).isoformat(),
        "dca_step_percent": max(float(template.get("dca_step_percent", 1.0)), 1.0),
        "max_dca_orders": safe_dca_orders(template),
        "dca_count": 0,
        "grid_levels": grid_levels,
        "grid_completed": 0,
        "entry_price": round(fill_price, 8),
        "current_price": round(fill_price, 8),
        "quantity": round(filled_amount, 8),
        "status": "RUNNING",
        "position_status": "OPEN",
        "risk": template.get("risk", "MEDIUM"),
        "unrealized_pnl": 0,
        "realized_pnl": 0,
        "total_pnl": 0,
        "trade_count": 1,
        "cycle_count": 0,
        "price_change_percent": 0,
        "auto_select": bool(auto_select),
        "auto_reentry": bool(auto_reentry),
        "trading_mode": get_trading_mode(),
        "last_action": "BUY_OPENED",
        "last_order_response": order_result,
        "loss_streak": 0,
        "win_streak": 0,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "orders": [
            make_order_log("BUY", selected_symbol, fill_price, filled_amount, None, "BOT_START")
        ],
    }

    bot_state["bots"].append(bot)

    return {
        "message": "Bot started safely",
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
        if bot.get("status") != "RUNNING":
            continue

        bot["cycle_count"] += 1

        safety_result = check_bot_safety(bot)

        if safety_result:
            actions.append({"bot_id": bot["id"], "action": safety_result})
            continue

        if not interval_allowed(bot):
            bot["last_action"] = "WAIT_INTERVAL"
            actions.append({"bot_id": bot["id"], "action": "WAIT_INTERVAL"})
            continue

        if bot.get("position_status") == "OPEN":
            price_change_percent = calculate_price_change_percent(bot)

            if bot["strategy"] == "DCA" and should_dca(bot, price_change_percent):
                result = add_dca_order(bot)
                actions.append({"bot_id": bot["id"], "action": "DCA_BUY", "result": result})
                continue

            if bot["strategy"] == "GRID":
                update_grid_progress(bot)

            if price_change_percent >= bot["tp_percent"]:
                close_result = close_position(bot, "TAKE_PROFIT")
                actions.append(
                    {
                        "bot_id": bot["id"],
                        "action": "TAKE_PROFIT",
                        "result": close_result,
                    }
                )

                if bot.get("auto_reentry") and bot.get("loss_streak", 0) == 0:
                    result = reopen_position(bot, reason="REENTRY_AFTER_PROFIT")
                    actions.append(
                        {
                            "bot_id": bot["id"],
                            "action": "REENTRY_AFTER_PROFIT",
                            "result": result,
                        }
                    )

            elif price_change_percent <= -abs(bot["sl_percent"]):
                close_result = close_position(bot, "STOP_LOSS")
                actions.append(
                    {
                        "bot_id": bot["id"],
                        "action": "STOP_LOSS",
                        "result": close_result,
                    }
                )

                bot["status"] = "PAUSED"
                bot["last_action"] = "PAUSED_AFTER_STOP_LOSS"
                actions.append(
                    {
                        "bot_id": bot["id"],
                        "action": "PAUSED_AFTER_STOP_LOSS",
                        "message": "Zarar sonrası otomatik tekrar giriş kapatıldı.",
                    }
                )

            else:
                bot["last_action"] = "HOLD"
                actions.append({"bot_id": bot["id"], "action": "HOLD"})

        elif bot.get("position_status") == "CLOSED":
            bot["last_action"] = "CLOSED_WAITING"
            actions.append({"bot_id": bot["id"], "action": "CLOSED_WAITING"})

        bot["updated_at"] = now_iso()

    return {
        "message": "Bot cycle completed safely",
        "mode": get_trading_mode(),
        "actions": actions,
        "bots": bot_state["bots"],
    }


def close_position(bot, reason):
    price = find_price(bot["symbol"]) or bot.get("current_price") or bot.get("entry_price")

    if price <= 0:
        bot["last_action"] = f"{reason}_FAILED_NO_PRICE"
        return {"error": "Kapanış için fiyat bulunamadı"}

    quantity = bot.get("quantity", 0)

    if quantity <= 0:
        bot["last_action"] = f"{reason}_FAILED_NO_QUANTITY"
        return {"error": "Kapanış için miktar bulunamadı"}

    order_result = execute_trade(bot["symbol"], "SELL", price, quantity)

    if not order_is_ok(order_result):
        bot["last_action"] = f"{reason}_FAILED_ORDER"
        bot["last_order_response"] = order_result
        return {
            "error": "SELL emri başarısız veya dolmadı. Pozisyon kapandı sayılmadı.",
            "order_response": order_result,
        }

    filled_amount = get_filled_amount(order_result) or quantity
    fill_price = get_fill_price(order_result) or price

    pnl = round((fill_price - bot["entry_price"]) * filled_amount, 4)

    bot["realized_pnl"] = round(bot.get("realized_pnl", 0) + pnl, 4)
    bot["total_pnl"] = round(bot["realized_pnl"], 4)
    bot["unrealized_pnl"] = 0
    bot["exit_price"] = round(fill_price, 8)
    bot["position_status"] = "CLOSED"
    bot["last_action"] = reason
    bot["last_order_response"] = order_result
    bot["orders"].append(make_order_log("SELL", bot["symbol"], fill_price, filled_amount, pnl, reason))
    set_next_interval(bot)

    if pnl < 0:
        bot["loss_streak"] = bot.get("loss_streak", 0) + 1
        bot["win_streak"] = 0
    else:
        bot["win_streak"] = bot.get("win_streak", 0) + 1
        bot["loss_streak"] = 0

    return {"message": reason, "pnl": pnl, "order_response": order_result}


def reopen_position(bot, reason="REENTRY"):
    if bot["trade_count"] >= bot["max_daily_trades"]:
        bot["status"] = "PAUSED"
        bot["last_action"] = "MAX_DAILY_TRADES_REACHED"
        return {"error": "Günlük işlem limiti doldu"}

    if bot.get("realized_pnl", 0) <= -abs(bot.get("daily_loss_limit_usd", 3)):
        bot["status"] = "PAUSED"
        bot["last_action"] = "DAILY_LOSS_LIMIT_REACHED"
        return {"error": "Günlük zarar limiti doldu"}

    if bot.get("loss_streak", 0) >= 1:
        bot["status"] = "PAUSED"
        bot["last_action"] = "REENTRY_BLOCKED_AFTER_LOSS"
        return {"error": "Zarar sonrası tekrar giriş güvenlik nedeniyle engellendi"}

    selected_symbol = select_best_symbol(bot["symbol"], bot["auto_select"], bot["strategy"])

    if not is_safe_symbol(selected_symbol):
        bot["last_action"] = "REENTRY_BLOCKED_RISKY_SYMBOL"
        return {"error": "Riskli token engellendi", "symbol": selected_symbol}

    price = find_price(selected_symbol)

    if price <= 0:
        bot["last_action"] = "REENTRY_FAILED_NO_PRICE"
        return {"error": "Yeni pozisyon için fiyat bulunamadı"}

    quantity = calculate_quantity(bot["amount_usd"], price)

    order_result = execute_trade(selected_symbol, "BUY", price, quantity)

    if not order_is_ok(order_result):
        bot["last_action"] = "REENTRY_FAILED_ORDER"
        bot["last_order_response"] = order_result
        return {
            "error": "REENTRY emri başarısız veya dolmadı.",
            "order_response": order_result,
        }

    filled_amount = get_filled_amount(order_result) or quantity
    fill_price = get_fill_price(order_result) or price

    bot["symbol"] = selected_symbol
    bot["entry_price"] = round(fill_price, 8)
    bot["current_price"] = round(fill_price, 8)
    bot["quantity"] = round(filled_amount, 8)
    bot["position_status"] = "OPEN"
    bot["trade_count"] += 1
    bot["dca_count"] = 0
    bot["unrealized_pnl"] = 0
    bot["price_change_percent"] = 0

    if bot["strategy"] == "GRID":
        bot["grid_levels"] = build_grid_levels(fill_price, 8, 1.5)
        bot["grid_completed"] = 0

    bot["last_action"] = reason
    bot["last_order_response"] = order_result
    bot["orders"].append(make_order_log("BUY", selected_symbol, fill_price, filled_amount, None, reason))
    set_next_interval(bot)

    return {
        "message": "New position opened safely",
        "symbol": selected_symbol,
        "order_response": order_result,
    }


def add_dca_order(bot):
    if bot.get("realized_pnl", 0) <= -abs(bot.get("daily_loss_limit_usd", 3)):
        bot["status"] = "PAUSED"
        bot["last_action"] = "DCA_BLOCKED_DAILY_LOSS"
        return {"error": "DCA engellendi. Günlük zarar limiti doldu."}

    if bot["dca_count"] >= bot["max_dca_orders"]:
        return {"error": "Maksimum DCA sayısına ulaşıldı"}

    price = find_price(bot["symbol"])

    if price <= 0:
        return {"error": "DCA için fiyat bulunamadı"}

    quantity = calculate_quantity(bot["amount_usd"], price)
    order_result = execute_trade(bot["symbol"], "BUY", price, quantity)

    if not order_is_ok(order_result):
        bot["last_action"] = "DCA_FAILED_ORDER"
        bot["last_order_response"] = order_result
        return {
            "error": "DCA emri başarısız veya dolmadı.",
            "order_response": order_result,
        }

    filled_amount = get_filled_amount(order_result) or quantity
    fill_price = get_fill_price(order_result) or price

    old_value = bot["entry_price"] * bot["quantity"]
    new_value = fill_price * filled_amount
    new_quantity = bot["quantity"] + filled_amount

    bot["entry_price"] = round((old_value + new_value) / new_quantity, 8)
    bot["quantity"] = round(new_quantity, 8)
    bot["current_price"] = round(fill_price, 8)
    bot["dca_count"] += 1
    bot["trade_count"] += 1
    bot["last_action"] = "DCA_BUY"
    bot["last_order_response"] = order_result
    bot["orders"].append(make_order_log("BUY", bot["symbol"], fill_price, filled_amount, None, "DCA"))
    set_next_interval(bot)

    return {"message": "DCA order opened safely", "order_response": order_result}


def refresh_bot_prices():
    for bot in bot_state["bots"]:
        if bot.get("position_status") != "OPEN":
            continue

        price = find_price(bot["symbol"])

        if price > 0:
            bot["current_price"] = round(price, 8)
            bot["unrealized_pnl"] = round(
                (price - bot["entry_price"]) * bot["quantity"],
                4,
            )
            bot["total_pnl"] = round(
                bot.get("realized_pnl", 0) + bot.get("unrealized_pnl", 0),
                4,
            )
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
    if bot["strategy"] != "DCA":
        return False

    if bot["dca_count"] >= bot["max_dca_orders"]:
        return False

    if bot.get("loss_streak", 0) >= 1:
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
    seconds = max(
        SAFE_MIN_INTERVAL_SECONDS,
        int(bot.get("min_interval_seconds", SAFE_MIN_INTERVAL_SECONDS)),
    )
    bot["next_allowed_trade_at"] = (now_dt() + timedelta(seconds=seconds)).isoformat()


def check_bot_safety(bot):
    if bot["trade_count"] >= bot["max_daily_trades"]:
        bot["status"] = "PAUSED"
        bot["last_action"] = "MAX_DAILY_TRADES_REACHED"
        return "PAUSED_MAX_TRADES"

    if bot.get("realized_pnl", 0) >= bot.get("daily_target_usd", 10):
        bot["status"] = "PAUSED"
        bot["last_action"] = "DAILY_TARGET_REACHED"
        return "PAUSED_TARGET_REACHED"

    if bot.get("realized_pnl", 0) <= -abs(bot.get("daily_loss_limit_usd", 3)):
        bot["status"] = "PAUSED"
        bot["last_action"] = "DAILY_LOSS_LIMIT_REACHED"
        return "PAUSED_LOSS_LIMIT"

    if not is_safe_symbol(bot.get("symbol", "")):
        bot["status"] = "PAUSED"
        bot["last_action"] = "RISKY_SYMBOL_BLOCKED"
        return "PAUSED_RISKY_SYMBOL"

    return None


def select_best_symbol(symbol, auto_select, strategy):
    if not auto_select and symbol != "AUTO":
        selected = symbol.upper()
        return selected if is_safe_symbol(selected) else "BTCUSDT"

    scan_all_market()
    best_items = get_scanner_results(300)["items"]

    active_symbols = {
        bot["symbol"]
        for bot in bot_state["bots"]
        if bot.get("status") == "RUNNING" and bot.get("position_status") == "OPEN"
    }

    candidates = []

    for item in best_items:
        item_symbol = item.get("symbol", "").upper()

        if not item_symbol:
            continue

        if item_symbol in active_symbols:
            continue

        if not is_safe_symbol(item_symbol):
            continue

        if not market_item_is_tradeable(item):
            continue

        if can_reenter(strategy, item, symbol):
            candidates.append(item)

    if candidates:
        candidates.sort(
            key=lambda x: (
                float(x.get("confidence", 0) or 0),
                float(x.get("volume_24h", 0) or 0),
            ),
            reverse=True,
        )
        return candidates[0]["symbol"]

    fallback = [
        item
        for item in best_items
        if is_safe_symbol(item.get("symbol", ""))
        and market_item_is_tradeable(item)
        and item.get("symbol") not in active_symbols
    ]

    if fallback:
        fallback.sort(
            key=lambda x: (
                float(x.get("volume_24h", 0) or 0),
                float(x.get("confidence", 0) or 0),
            ),
            reverse=True,
        )
        return fallback[0]["symbol"]

    return "BTCUSDT"


def market_item_is_tradeable(item):
    price = float(item.get("price", 0) or 0)
    volume = float(item.get("volume_24h", 0) or 0)
    change = float(item.get("change_24h", 0) or 0)
    confidence = float(item.get("confidence", 0) or 0)

    if price <= 0:
        return False

    if volume < 100_000:
        return False

    if abs(change) > 25:
        return False

    if confidence < 45:
        return False

    return True


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
        "price": round(float(price), 8),
        "quantity": round(float(quantity), 8),
        "value": round(float(price) * float(quantity), 4),
        "pnl": pnl,
        "mode": get_trading_mode(),
        "created_at": now_iso(),
        "reason": reason,
    }


def get_gateio_order_data(order_result):
    if not isinstance(order_result, dict):
        return {}

    exchange_response = order_result.get("exchange_response")

    if not isinstance(exchange_response, dict):
        return {}

    nested_response = exchange_response.get("exchange_response")

    if not isinstance(nested_response, dict):
        return {}

    data = nested_response.get("data", {})

    if isinstance(data, dict):
        return data

    return {}


def get_filled_amount(order_result):
    data = get_gateio_order_data(order_result)

    try:
        return float(data.get("filled_amount", 0) or 0)
    except Exception:
        return 0


def get_fill_price(order_result):
    data = get_gateio_order_data(order_result)

    # Gate.io'da doğru birim fiyat genelde avg_deal_price alanıdır.
    try:
        avg_deal_price = float(data.get("avg_deal_price", 0) or 0)
        if avg_deal_price > 0:
            return avg_deal_price
    except Exception:
        pass

    # Eğer avg_deal_price yoksa toplam tutarı / dolan miktarı kullan.
    try:
        filled_total = float(data.get("filled_total", 0) or 0)
        filled_amount = float(data.get("filled_amount", 0) or 0)

        if filled_total > 0 and filled_amount > 0:
            return filled_total / filled_amount
    except Exception:
        pass

    # Son çare olarak order price kullanılır.
    try:
        order_price = float(data.get("price", 0) or 0)
        if order_price > 0:
            return order_price
    except Exception:
        pass

    return 0


def order_is_ok(order_result):
    if not order_result:
        return False

    if order_result.get("error"):
        return False

    mode = str(order_result.get("mode", "")).upper()

    # PAPER modda exchange response olmayabilir.
    # Hata yoksa paper emri başarılı kabul edilir.
    if mode == "PAPER":
        return True

    exchange_response = order_result.get("exchange_response")

    if not isinstance(exchange_response, dict):
        return False

    if exchange_response.get("ok") is False:
        return False

    nested_response = exchange_response.get("exchange_response")

    if not isinstance(nested_response, dict):
        return False

    if nested_response.get("ok") is False:
        return False

    data = nested_response.get("data", {})

    if not isinstance(data, dict):
        return False

    status = str(data.get("status", "")).lower()
    finish_as = str(data.get("finish_as", "")).lower()

    try:
        filled_amount = float(data.get("filled_amount", 0) or 0)
    except Exception:
        filled_amount = 0

    # En kritik kontrol:
    # Gate.io 201 döndürse bile filled_amount 0 ise işlem gerçekleşmedi demektir.
    if filled_amount <= 0:
        return False

    # Tam iptal olmuş ve hiç dolmamış emir başarısızdır.
    if status == "cancelled" and filled_amount <= 0:
        return False

    # IOC ile kısmi/tam dolum olabilir. filled_amount > 0 ise kabul ediyoruz.
    if finish_as == "ioc" and filled_amount > 0:
        return True

    if status in ["closed", "finished"] and filled_amount > 0:
        return True

    return filled_amount > 0


def is_safe_symbol(symbol):
    clean = symbol.upper().replace("/", "").replace("_", "")

    if not clean.endswith("USDT"):
        return False

    for blocked in BLOCKED_SYMBOL_PARTS:
        if blocked in clean:
            return False

    return True


def calculate_quantity(amount_usd, price):
    if price <= 0:
        return 0

    quantity = float(amount_usd) / float(price)

    return round(quantity, 8)


def safe_amount(amount_usd):
    amount = float(amount_usd or 0)

    if amount <= 0:
        amount = 10

    if amount > SAFE_MAX_AMOUNT_USD:
        amount = SAFE_MAX_AMOUNT_USD

    return amount


def safe_daily_loss_limit(value):
    loss = float(value or 3)

    if loss <= 0:
        loss = 3

    if loss > 5:
        loss = 5

    return loss


def safe_max_daily_trades(value):
    trades = int(value or SAFE_MAX_DAILY_TRADES)

    if trades <= 0:
        trades = 5

    if trades > SAFE_MAX_DAILY_TRADES:
        trades = SAFE_MAX_DAILY_TRADES

    return trades


def safe_tp(value):
    tp = float(value or SAFE_DEFAULT_TP_PERCENT)

    if tp < 0.30:
        tp = SAFE_DEFAULT_TP_PERCENT

    if tp > 3:
        tp = 3

    return tp


def safe_sl(value):
    sl = float(value or SAFE_DEFAULT_SL_PERCENT)

    if sl < 0.20:
        sl = SAFE_DEFAULT_SL_PERCENT

    if sl > 1:
        sl = 1

    return sl


def safe_dca_orders(template):
    if template.get("strategy") != "DCA":
        return 0

    return min(int(template.get("max_dca_orders", 1)), 1)