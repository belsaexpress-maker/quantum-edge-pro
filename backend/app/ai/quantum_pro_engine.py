from datetime import datetime, timedelta

from app.ai.opportunity_engine import scan_opportunities
from app.market_engine.market_manager import get_market_snapshot
from app.trading.trade_executor import execute_trade, get_trading_mode
from app.trading.gateio_client import get_best_bid_ask


pro_state = {"bots": []}


SAFE_MAX_TRADES = 20
SAFE_MIN_INTERVAL_SECONDS = 90
SAFE_MAX_BALANCE_PER_BOT = 30
SAFE_MAX_LOSS_PERCENT = 3
SAFE_TARGET_PERCENT = 5


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


TESTNET_ALLOWED_SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "WLDUSDT",
]


PRO_BOTS = [
    {
        "id": "qe_spot_1",
        "name": "QuantumEdge Pro Spot 1",
        "market": "SPOT",
        "enabled": True,
        "risk": "Safe",
        "min_score": 82,
        "tp": 0.70,
        "sl": 0.40,
        "max_trades": 12,
        "trend_hold_score": 88,
        "min_interval_seconds": 120,
    },
    {
        "id": "qe_spot_2",
        "name": "QuantumEdge Pro Spot 2",
        "market": "SPOT",
        "enabled": True,
        "risk": "Fast",
        "min_score": 72,
        "tp": 0.60,
        "sl": 0.35,
        "max_trades": 15,
        "trend_hold_score": 85,
        "min_interval_seconds": 90,
    },
    {
        "id": "qe_futures_1",
        "name": "QuantumEdge Pro Futures 1",
        "market": "FUTURES",
        "enabled": False,
        "risk": "Balanced",
        "min_score": 85,
        "tp": 0.80,
        "sl": 0.45,
        "max_trades": 10,
        "trend_hold_score": 88,
        "min_interval_seconds": 120,
        "disabled_reason": "Futures executor henuz baglanmadi. Spot executor ile futures calistirilmaz.",
    },
    {
        "id": "qe_futures_2",
        "name": "QuantumEdge Pro Futures 2",
        "market": "FUTURES",
        "enabled": False,
        "risk": "Aggressive",
        "min_score": 78,
        "tp": 0.90,
        "sl": 0.50,
        "max_trades": 8,
        "trend_hold_score": 86,
        "min_interval_seconds": 150,
        "disabled_reason": "Futures executor henuz baglanmadi. Spot executor ile futures calistirilmaz.",
    },
]


def now():
    return datetime.utcnow().isoformat()


def now_dt():
    return datetime.utcnow()


def list_quantum_pro_bots():
    refresh_prices()

    return {
        "mode": get_trading_mode(),
        "safety": {
            "live_enabled": False,
            "max_trades": SAFE_MAX_TRADES,
            "max_balance_per_bot": SAFE_MAX_BALANCE_PER_BOT,
            "max_loss_percent": SAFE_MAX_LOSS_PERCENT,
            "blocked_leveraged_tokens": BLOCKED_SYMBOL_PARTS,
            "testnet_allowed_symbols": TESTNET_ALLOWED_SYMBOLS,
            "futures_enabled": False,
        },
        "templates": PRO_BOTS,
        "running": pro_state["bots"],
    }


def start_quantum_pro_bot(
    bot_id,
    balance=30,
    target_percent=SAFE_TARGET_PERCENT,
    max_loss_percent=SAFE_MAX_LOSS_PERCENT,
    compound=True,
):
    template = next((b for b in PRO_BOTS if b["id"] == bot_id), None)

    if not template:
        return {"error": "QuantumEdge Pro bot bulunamadi"}

    if not template.get("enabled", False):
        return {
            "error": "Bu bot guvenlik icin henuz aktif degil",
            "bot_id": bot_id,
            "market": template.get("market"),
            "reason": template.get("disabled_reason", "Bot disabled"),
        }

    balance = safe_balance(balance)
    target_percent = safe_target_percent(target_percent)
    max_loss_percent = safe_max_loss_percent(max_loss_percent)

    setup = select_setup(template)

    if not setup:
        return {"error": "Opportunity Engine uygun guvenli firsat bulamadi"}

    symbol = setup["symbol"]

    if not is_safe_symbol(symbol):
        return {"error": "Riskli / kaldiracli token engellendi", "symbol": symbol}

    if not symbol_allowed_for_mode(symbol):
        return {
            "error": "Bu sembol mevcut trading mode icin izinli degil",
            "symbol": symbol,
            "mode": get_trading_mode(),
        }

    if not exchange_pair_is_tradeable(symbol):
        return {
            "error": "Gate.io orderbook dogrulanamadi. Emir gonderilmedi.",
            "symbol": symbol,
            "mode": get_trading_mode(),
        }

    price = get_price(symbol)

    if price <= 0:
        return {"error": "Canli fiyat bulunamadi", "symbol": symbol}

    trade_amount = calculate_trade_amount(balance, setup["opportunity_score"])
    quantity = calculate_quantity(trade_amount, price)

    if quantity <= 0:
        return {"error": "Miktar hesaplanamadi"}

    order = execute_trade(symbol, "BUY", price, quantity)

    if not order_is_ok(order):
        return {
            "error": "PRO BUY emri basarisiz veya dolmadi. Bot pozisyon acmadi.",
            "symbol": symbol,
            "order_response": order,
        }

    filled_amount = get_filled_amount(order) or quantity
    fill_price = get_fill_price(order) or price

    trend_hold = detect_trend_hold(template, setup)

    bot = {
        "id": len(pro_state["bots"]) + 1,
        "bot_id": bot_id,
        "name": template["name"],
        "market": template["market"],
        "risk": template["risk"],
        "symbol": symbol,
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
        "compound": bool(compound),
        "entry_price": round(fill_price, 8),
        "current_price": round(fill_price, 8),
        "highest_price": round(fill_price, 8),
        "quantity": round(filled_amount, 8),
        "trade_amount": round(fill_price * filled_amount, 4),
        "tp_percent": safe_tp(template.get("tp")),
        "sl_percent": safe_sl(template.get("sl")),
        "trailing_stop_percent": 0.45,
        "trend_hold_mode": trend_hold["enabled"],
        "trend_hold_reason": trend_hold["reason"],
        "exit_mode": "SELL_SIGNAL" if trend_hold["enabled"] else "MICRO_TP",
        "max_trades": safe_max_trades(template.get("max_trades")),
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
        "trade_count": 1,
        "consecutive_losses": 0,
        "realized_pnl": 0,
        "unrealized_pnl": 0,
        "total_pnl": 0,
        "daily_profit_percent": 0,
        "price_change_percent": 0,
        "ai_score": setup["ai_score"],
        "smart_money_score": setup["smart_money_score"],
        "opportunity_score": setup["opportunity_score"],
        "reasons": setup["reasons"],
        "last_action": "PRO_BUY_OPENED",
        "last_order_response": order,
        "orders": [
            order_log(
                "BUY",
                symbol,
                fill_price,
                filled_amount,
                None,
                "PRO_START",
                setup,
                trend_hold["enabled"],
            )
        ],
        "created_at": now(),
        "updated_at": now(),
    }

    pro_state["bots"].append(bot)

    return {
        "message": "QuantumEdge Pro bot started safely",
        "mode": get_trading_mode(),
        "bot": bot,
        "order_response": order,
    }


def stop_quantum_pro_bot(bot_id):
    refresh_prices()
    bot = next((b for b in pro_state["bots"] if b["id"] == bot_id), None)

    if not bot:
        return {"error": "Bot bulunamadi"}

    if bot["position_status"] == "OPEN":
        close_position(bot, "MANUAL_CLOSE")

    bot["status"] = "STOPPED"
    bot["position_status"] = "CLOSED"
    bot["last_action"] = "STOPPED"
    bot["updated_at"] = now()

    return {
        "message": "QuantumEdge Pro bot stopped",
        "mode": get_trading_mode(),
        "bot": bot,
    }


def run_quantum_pro_cycle():
    refresh_prices()
    actions = []

    for bot in pro_state["bots"]:
        if bot.get("status") != "RUNNING":
            continue

        safety_result = check_bot_safety(bot)

        if safety_result:
            actions.append({"bot": bot["id"], "action": safety_result})
            continue

        if not interval_allowed(bot):
            bot["last_action"] = "WAIT_INTERVAL"
            actions.append({"bot": bot["id"], "action": "WAIT_INTERVAL"})
            continue

        price_change = price_change_percent(bot)

        if bot["current_price"] > bot.get("highest_price", 0):
            bot["highest_price"] = bot["current_price"]

        if bot["trend_hold_mode"]:
            exit_signal = detect_sell_signal(bot)

            if exit_signal["sell"]:
                close_result = close_position(bot, exit_signal["reason"])
                actions.append(
                    {
                        "bot": bot["id"],
                        "action": exit_signal["reason"],
                        "result": close_result,
                    }
                )

                if close_result.get("pnl", 0) > 0:
                    reentry = reopen_position(bot, "REENTRY_AFTER_PROFIT")
                    actions.append(
                        {
                            "bot": bot["id"],
                            "action": "REENTRY_AFTER_PROFIT",
                            "result": reentry,
                        }
                    )
                else:
                    bot["status"] = "PAUSED"
                    bot["last_action"] = "PAUSED_AFTER_LOSS"

            else:
                bot["last_action"] = "TREND_HOLD_WAIT_SELL_SIGNAL"
                actions.append({"bot": bot["id"], "action": "TREND_HOLD"})

        else:
            if price_change >= bot["tp_percent"]:
                close_result = close_position(bot, "MICRO_TAKE_PROFIT")
                actions.append(
                    {
                        "bot": bot["id"],
                        "action": "MICRO_TAKE_PROFIT",
                        "result": close_result,
                    }
                )

                if close_result.get("pnl", 0) > 0:
                    reentry = reopen_position(bot, "REENTRY_AFTER_PROFIT")
                    actions.append(
                        {
                            "bot": bot["id"],
                            "action": "REENTRY_AFTER_PROFIT",
                            "result": reentry,
                        }
                    )

            elif price_change <= -abs(bot["sl_percent"]):
                close_result = close_position(bot, "STOP_LOSS")
                bot["status"] = "PAUSED"
                bot["last_action"] = "PAUSED_AFTER_STOP_LOSS"

                actions.append(
                    {
                        "bot": bot["id"],
                        "action": "STOP_LOSS_PAUSED",
                        "result": close_result,
                    }
                )

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

    return {
        "message": "Quantum Pro cycle completed safely",
        "mode": get_trading_mode(),
        "actions": actions,
        "running": pro_state["bots"],
    }


def close_position(bot, reason):
    price = get_price(bot["symbol"]) or bot.get("current_price") or bot.get("entry_price")

    if price <= 0:
        bot["last_action"] = f"{reason}_FAILED_NO_PRICE"
        return {"error": "Kapanis icin fiyat bulunamadi"}

    quantity = bot.get("quantity", 0)

    if quantity <= 0:
        bot["last_action"] = f"{reason}_FAILED_NO_QUANTITY"
        return {"error": "Kapanis icin miktar bulunamadi"}

    order = execute_trade(bot["symbol"], "SELL", price, quantity)

    if not order_is_ok(order):
        bot["last_action"] = f"{reason}_FAILED_ORDER"
        bot["last_order_response"] = order
        return {
            "error": "PRO SELL emri basarisiz veya dolmadi. Pozisyon kapandi sayilmadi.",
            "order_response": order,
        }

    filled_amount = get_filled_amount(order) or quantity
    fill_price = get_fill_price(order) or price

    pnl = round((fill_price - bot["entry_price"]) * filled_amount, 4)

    bot["realized_pnl"] = round(bot["realized_pnl"] + pnl, 4)
    bot["portfolio_balance"] = round(bot["portfolio_balance"] + pnl, 4)
    bot["current_equity"] = round(bot["portfolio_balance"], 4)
    bot["total_pnl"] = round(bot["realized_pnl"], 4)
    bot["unrealized_pnl"] = 0
    bot["daily_profit_percent"] = calculate_daily_profit_percent(bot)
    bot["position_status"] = "CLOSED"
    bot["exit_price"] = round(fill_price, 8)
    bot["last_action"] = reason
    bot["last_order_response"] = order
    bot["orders"].append(
        order_log(
            "SELL",
            bot["symbol"],
            fill_price,
            filled_amount,
            pnl,
            reason,
            bot,
            bot["trend_hold_mode"],
        )
    )
    set_next_interval(bot)

    if pnl < 0:
        bot["consecutive_losses"] += 1
    else:
        bot["consecutive_losses"] = 0

    return {"message": reason, "pnl": pnl, "order_response": order}


def reopen_position(bot, reason="REENTRY"):
    if bot.get("consecutive_losses", 0) >= 1:
        bot["status"] = "PAUSED"
        bot["last_action"] = "REENTRY_BLOCKED_AFTER_LOSS"
        return {"error": "Zarar sonrasi reentry guvenlik nedeniyle engellendi"}

    if bot["trade_count"] >= bot["max_trades"]:
        bot["status"] = "PAUSED"
        bot["last_action"] = "MAX_TRADES_REACHED"
        return {"error": "Maksimum islem limiti doldu"}

    loss_limit = bot["cycle_start_balance"] * bot["max_loss_percent"] / 100

    if bot["total_pnl"] <= -abs(loss_limit):
        bot["status"] = "LOCKED"
        bot["last_action"] = "MAX_DAILY_LOSS"
        return {"error": "Zarar limiti doldu"}

    template = next((b for b in PRO_BOTS if b["id"] == bot["bot_id"]), None)

    if not template or not template.get("enabled", False):
        return {"error": "Template aktif degil"}

    setup = select_setup(template)

    if not setup:
        bot["last_action"] = "NO_OPPORTUNITY_SETUP"
        return {"error": "Opportunity Engine yeni setup bulamadi"}

    symbol = setup["symbol"]

    if not is_safe_symbol(symbol):
        return {"error": "Riskli token engellendi", "symbol": symbol}

    if not symbol_allowed_for_mode(symbol):
        return {"error": "Bu sembol mevcut mode icin izinli degil", "symbol": symbol}

    if not exchange_pair_is_tradeable(symbol):
        return {"error": "Gate.io orderbook dogrulanamadi", "symbol": symbol}

    price = get_price(symbol)

    if price <= 0:
        return {"error": "Fiyat bulunamadi"}

    balance = bot["portfolio_balance"] if bot["compound"] else bot["cycle_start_balance"]
    amount = calculate_trade_amount(balance, setup["opportunity_score"])
    quantity = calculate_quantity(amount, price)

    order = execute_trade(symbol, "BUY", price, quantity)

    if not order_is_ok(order):
        bot["last_action"] = "REENTRY_FAILED_ORDER"
        bot["last_order_response"] = order
        return {
            "error": "Reentry emri basarisiz veya dolmadi",
            "order_response": order,
        }

    filled_amount = get_filled_amount(order) or quantity
    fill_price = get_fill_price(order) or price
    trend_hold = detect_trend_hold(template, setup)

    bot["symbol"] = symbol
    bot["entry_price"] = round(fill_price, 8)
    bot["current_price"] = round(fill_price, 8)
    bot["highest_price"] = round(fill_price, 8)
    bot["quantity"] = round(filled_amount, 8)
    bot["trade_amount"] = round(fill_price * filled_amount, 4)
    bot["position_status"] = "OPEN"
    bot["trade_count"] += 1
    bot["ai_score"] = setup["ai_score"]
    bot["smart_money_score"] = setup["smart_money_score"]
    bot["opportunity_score"] = setup["opportunity_score"]
    bot["reasons"] = setup["reasons"]
    bot["trend_hold_mode"] = trend_hold["enabled"]
    bot["trend_hold_reason"] = trend_hold["reason"]
    bot["exit_mode"] = "SELL_SIGNAL" if trend_hold["enabled"] else "MICRO_TP"
    bot["last_action"] = reason
    bot["last_order_response"] = order
    bot["orders"].append(
        order_log(
            "BUY",
            symbol,
            fill_price,
            filled_amount,
            None,
            reason,
            setup,
            trend_hold["enabled"],
        )
    )
    set_next_interval(bot)

    return {"message": "Reentry opened safely", "order_response": order}


def select_setup(template):
    opportunities = scan_opportunities(200).get("items", [])

    active = {
        b["symbol"]
        for b in pro_state["bots"]
        if b.get("status") == "RUNNING" and b.get("position_status") == "OPEN"
    }

    candidates = []

    for item in opportunities:
        setup = normalize_setup(item)

        symbol = setup["symbol"]
        score = setup["opportunity_score"]
        decision = setup["decision"]

        if not symbol:
            continue

        if symbol in active:
            continue

        if not symbol_allowed_for_mode(symbol):
            continue

        if not is_safe_symbol(symbol):
            continue

        if not setup_is_tradeable(setup):
            continue

        if not exchange_pair_is_tradeable(symbol):
            continue

        if score >= template["min_score"] and decision in ["STRONG_LONG", "LONG", "WATCH"]:
            candidates.append(setup)

    if candidates:
        candidates.sort(
            key=lambda x: (
                float(x.get("opportunity_score", 0) or 0),
                float(x.get("volume_24h", 0) or 0),
            ),
            reverse=True,
        )
        return candidates[0]

    fallback = []

    for item in opportunities:
        setup = normalize_setup(item)
        symbol = setup.get("symbol", "")

        if symbol in active:
            continue

        if not symbol_allowed_for_mode(symbol):
            continue

        if not is_safe_symbol(symbol):
            continue

        if not setup_is_tradeable(setup):
            continue

        if not exchange_pair_is_tradeable(symbol):
            continue

        fallback.append(setup)

    if fallback:
        fallback.sort(
            key=lambda x: (
                float(x.get("volume_24h", 0) or 0),
                float(x.get("opportunity_score", 0) or 0),
            ),
            reverse=True,
        )
        return fallback[0]

    if get_trading_mode() == "TESTNET":
        for symbol in TESTNET_ALLOWED_SYMBOLS:
            if symbol in active:
                continue

            if exchange_pair_is_tradeable(symbol):
                return build_safe_testnet_setup(symbol)

    return None


def normalize_setup(item):
    item = item or {}

    return {
        "symbol": str(item.get("symbol", "")).upper(),
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
    score = float(setup.get("opportunity_score", 0) or 0)
    change = float(setup.get("change_24h", 0) or 0)
    volume = float(setup.get("volume_24h", 0) or 0)

    if score >= template.get("trend_hold_score", 88) and 1.2 < change <= 12 and volume > 500_000:
        return {"enabled": True, "reason": "Strong uptrend detected by Opportunity Engine"}

    return {"enabled": False, "reason": "Micro TP mode: trend strength not enough"}


def maybe_enable_trend_hold(bot):
    opportunities = scan_opportunities(200).get("items", [])
    item = next((x for x in opportunities if x.get("symbol") == bot["symbol"]), None)

    if not item:
        return {"enabled": False, "reason": "No opportunity data"}

    opportunity_score = float(item.get("opportunity_score", 0) or 0)

    if opportunity_score >= 88 and bot["unrealized_pnl"] > 0:
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

    if item and float(item.get("opportunity_score", 0) or 0) < 60:
        return {"sell": True, "reason": "OPPORTUNITY_SCORE_WEAKENED"}

    return {"sell": False, "reason": "HOLD_TREND"}


def calculate_trade_amount(balance, score):
    balance = safe_balance(balance)
    score = float(score or 0)

    if score >= 90:
        risk = 0.18
    elif score >= 75:
        risk = 0.12
    elif score >= 60:
        risk = 0.08
    else:
        risk = 0.05

    amount = round(balance * risk, 2)

    return max(5, min(amount, SAFE_MAX_BALANCE_PER_BOT))


def calculate_quantity(amount, price):
    if price <= 0:
        return 0

    return round(float(amount) / float(price), 8)


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

            bot["unrealized_pnl"] = round((price - bot["entry_price"]) * bot["quantity"], 4)
            bot["current_equity"] = round(bot["portfolio_balance"] + bot["unrealized_pnl"], 4)
            bot["total_pnl"] = round(bot["realized_pnl"] + bot["unrealized_pnl"], 4)
            bot["daily_profit_percent"] = calculate_daily_profit_percent(bot)
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
        "price": round(float(price), 8),
        "quantity": round(float(quantity), 8),
        "value": round(float(price) * float(quantity), 4),
        "pnl": pnl,
        "mode": get_trading_mode(),
        "ai_score": source.get("ai_score", 0),
        "smart_money_score": source.get("smart_money_score", 0),
        "opportunity_score": source.get("opportunity_score", 0),
        "trend_hold": trend_hold,
        "created_at": now(),
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

    try:
        avg_deal_price = float(data.get("avg_deal_price", 0) or 0)

        if avg_deal_price > 0:
            return avg_deal_price
    except Exception:
        pass

    try:
        filled_total = float(data.get("filled_total", 0) or 0)
        filled_amount = float(data.get("filled_amount", 0) or 0)

        if filled_total > 0 and filled_amount > 0:
            return filled_total / filled_amount
    except Exception:
        pass

    try:
        price = float(data.get("price", 0) or 0)

        if price > 0:
            return price
    except Exception:
        pass

    return 0


def order_is_ok(order_result):
    if not order_result:
        return False

    if order_result.get("error"):
        return False

    mode = str(order_result.get("mode", "")).upper()

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

    try:
        filled_amount = float(data.get("filled_amount", 0) or 0)
    except Exception:
        filled_amount = 0

    if filled_amount <= 0:
        return False

    return True


def interval_allowed(bot):
    value = bot.get("next_allowed_trade_at")

    if not value:
        return True

    try:
        return now_dt() >= datetime.fromisoformat(value)
    except Exception:
        return True


def set_next_interval(bot):
    seconds = max(SAFE_MIN_INTERVAL_SECONDS, int(bot.get("min_interval_seconds", SAFE_MIN_INTERVAL_SECONDS)))
    bot["next_allowed_trade_at"] = (now_dt() + timedelta(seconds=seconds)).isoformat()


def check_bot_safety(bot):
    if bot["trade_count"] >= bot["max_trades"]:
        bot["status"] = "PAUSED"
        bot["last_action"] = "MAX_TRADES_REACHED"
        return "PAUSED_MAX_TRADES"

    if bot["consecutive_losses"] >= 2:
        bot["status"] = "LOCKED"
        bot["last_action"] = "LOCKED_2_LOSSES"
        return "LOCKED_2_LOSSES"

    loss_limit = bot["cycle_start_balance"] * bot["max_loss_percent"] / 100

    if bot["total_pnl"] <= -abs(loss_limit):
        bot["status"] = "LOCKED"
        bot["last_action"] = "MAX_DAILY_LOSS"
        return "MAX_DAILY_LOSS"

    target_profit = bot["cycle_start_balance"] * bot["target_percent"] / 100

    if bot["realized_pnl"] >= target_profit:
        reset_cycle(bot)
        return "TARGET_REACHED_NEW_CYCLE"

    if not is_safe_symbol(bot.get("symbol", "")):
        bot["status"] = "PAUSED"
        bot["last_action"] = "RISKY_SYMBOL_BLOCKED"
        return "RISKY_SYMBOL_BLOCKED"

    return None


def calculate_daily_profit_percent(bot):
    start = float(bot.get("cycle_start_balance", 0) or 0)

    if start <= 0:
        return 0

    current = float(bot.get("current_equity", bot.get("portfolio_balance", start)) or start)

    return round(((current - start) / start) * 100, 4)


def setup_is_tradeable(setup):
    symbol = setup.get("symbol", "")
    change = float(setup.get("change_24h", 0) or 0)
    volume = float(setup.get("volume_24h", 0) or 0)
    score = float(setup.get("opportunity_score", 0) or 0)

    if not is_safe_symbol(symbol):
        return False

    if volume < 100_000:
        return False

    if abs(change) > 25:
        return False

    if score < 50:
        return False

    return True


def is_safe_symbol(symbol):
    clean = str(symbol).upper().replace("/", "").replace("_", "")

    if not clean.endswith("USDT"):
        return False

    for blocked in BLOCKED_SYMBOL_PARTS:
        if blocked in clean:
            return False

    return True


def symbol_allowed_for_mode(symbol):
    clean = str(symbol).upper().replace("/", "").replace("_", "")

    if get_trading_mode() == "TESTNET":
        return clean in TESTNET_ALLOWED_SYMBOLS

    return True


def exchange_pair_is_tradeable(symbol):
    result = get_best_bid_ask(symbol)

    return bool(result.get("ok"))


def build_safe_testnet_setup(symbol):
    return {
        "symbol": symbol.upper(),
        "side": "LONG",
        "ai_score": 70,
        "smart_money_score": 70,
        "opportunity_score": 82,
        "decision": "WATCH",
        "change_24h": 0,
        "volume_24h": 1_000_000,
        "reasons": [
            "TESTNET guvenli fallback paritesi",
            "Gate.io orderbook dogrulandi",
            "Opportunity Engine uygun testnet paritesi bulamadi",
        ],
        "raw": {
            "source": "TESTNET_SAFE_FALLBACK",
            "symbol": symbol.upper(),
        },
    }


def safe_balance(value):
    balance = float(value or 30)

    if balance <= 0:
        balance = 30

    if balance > SAFE_MAX_BALANCE_PER_BOT:
        balance = SAFE_MAX_BALANCE_PER_BOT

    return balance


def safe_target_percent(value):
    target = float(value or SAFE_TARGET_PERCENT)

    if target <= 0:
        target = SAFE_TARGET_PERCENT

    if target > 15:
        target = 15

    return target


def safe_max_loss_percent(value):
    loss = float(value or SAFE_MAX_LOSS_PERCENT)

    if loss <= 0:
        loss = SAFE_MAX_LOSS_PERCENT

    if loss > SAFE_MAX_LOSS_PERCENT:
        loss = SAFE_MAX_LOSS_PERCENT

    return loss


def safe_tp(value):
    tp = float(value or 0.7)

    if tp < 0.4:
        tp = 0.7

    if tp > 2:
        tp = 2

    return tp


def safe_sl(value):
    sl = float(value or 0.4)

    if sl < 0.25:
        sl = 0.4

    if sl > 1:
        sl = 1

    return sl


def safe_max_trades(value):
    trades = int(value or SAFE_MAX_TRADES)

    if trades <= 0:
        trades = 5

    if trades > SAFE_MAX_TRADES:
        trades = SAFE_MAX_TRADES

    return trades