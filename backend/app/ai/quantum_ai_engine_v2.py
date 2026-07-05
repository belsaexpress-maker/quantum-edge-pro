import math
import time
import requests
from datetime import datetime

from app.market_engine.market_manager import get_market_snapshot
from app.trading.gateio_client import get_best_bid_ask


GATEIO_BASE_URL = "https://api.gateio.ws/api/v4"

TIMEFRAMES = ["1m", "5m", "15m", "1h"]

BLOCKED_SYMBOL_PARTS = [
    "3L", "3S", "5L", "5S", "BULL", "BEAR", "UPUSDT", "DOWNUSDT"
]

engine_memory = {
    "trades": [],
    "bot_scores": {},
    "symbol_scores": {},
    "last_scan": None,
}


def now():
    return datetime.utcnow().isoformat()


def run_quantum_ai_v2_scan(limit: int = 50):
    snapshot = get_market_snapshot()
    coins = snapshot.get("crypto", [])

    results = []

    for coin in coins[:limit]:
        symbol = coin.get("symbol", "")

        if not is_safe_symbol(symbol):
            continue

        price = float(coin.get("price", 0) or 0)
        volume = float(coin.get("volume_24h", 0) or 0)
        change = float(coin.get("change_24h", 0) or 0)

        if price <= 0 or volume <= 0:
            continue

        mtf = multi_timeframe_analysis(symbol)
        trend = trend_filter(mtf)
        volatility = volatility_filter(mtf)
        liquidity = liquidity_analysis(symbol, volume)
        orderbook = orderbook_pressure(symbol)
        fee = fee_optimization(symbol)
        correlation = position_correlation(symbol)
        learning = learning_score(symbol)

        score = calculate_quantum_score(
            trend=trend,
            volatility=volatility,
            liquidity=liquidity,
            orderbook=orderbook,
            fee=fee,
            correlation=correlation,
            learning=learning,
            change_24h=change,
            volume_24h=volume,
        )

        decision = build_decision(score, trend, volatility, liquidity, orderbook, fee)

        results.append(
            {
                "symbol": symbol,
                "price": price,
                "volume_24h": volume,
                "change_24h": change,
                "quantum_score": score,
                "decision": decision,
                "multi_timeframe": mtf,
                "trend_filter": trend,
                "volatility_filter": volatility,
                "liquidity": liquidity,
                "orderbook_pressure": orderbook,
                "fee_optimization": fee,
                "correlation": correlation,
                "learning": learning,
                "dynamic_tp_sl": dynamic_tp_sl(score, volatility, trend),
                "created_at": now(),
            }
        )

    results.sort(key=lambda x: x["quantum_score"], reverse=True)

    engine_memory["last_scan"] = {
        "time": now(),
        "count": len(results),
        "items": results,
    }

    return {
        "engine": "Quantum AI Engine v2",
        "mode": "analysis",
        "count": len(results),
        "items": results,
    }


def multi_timeframe_analysis(symbol: str):
    data = {}

    for tf in TIMEFRAMES:
        candles = get_candles(symbol, tf, limit=80)

        if not candles:
            data[tf] = empty_tf(tf)
            continue

        closes = [c["close"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        volumes = [c["volume"] for c in candles]

        ema_fast = ema(closes, 9)
        ema_slow = ema(closes, 21)
        rsi_value = rsi(closes, 14)
        atr_value = atr(highs, lows, closes, 14)
        macd_value = macd(closes)

        trend = "BULLISH" if ema_fast > ema_slow else "BEARISH"
        strength = abs((ema_fast - ema_slow) / ema_slow * 100) if ema_slow else 0

        data[tf] = {
            "timeframe": tf,
            "close": closes[-1],
            "ema_fast": round(ema_fast, 8),
            "ema_slow": round(ema_slow, 8),
            "rsi": round(rsi_value, 2),
            "atr": round(atr_value, 8),
            "macd": macd_value,
            "trend": trend,
            "trend_strength": round(strength, 4),
            "volume_avg": round(sum(volumes[-20:]) / max(len(volumes[-20:]), 1), 4),
        }

    bullish_count = len([x for x in data.values() if x["trend"] == "BULLISH"])

    return {
        "frames": data,
        "bullish_count": bullish_count,
        "alignment": round((bullish_count / len(TIMEFRAMES)) * 100, 2),
        "overall": "BULLISH" if bullish_count >= 3 else "MIXED" if bullish_count == 2 else "BEARISH",
    }


def trend_filter(mtf):
    alignment = mtf.get("alignment", 0)
    overall = mtf.get("overall", "MIXED")

    if overall == "BULLISH" and alignment >= 75:
        return {"score": 90, "status": "STRONG_TREND", "allow": True}

    if overall == "MIXED" and alignment >= 50:
        return {"score": 60, "status": "WEAK_TREND", "allow": True}

    return {"score": 25, "status": "NO_TREND", "allow": False}


def volatility_filter(mtf):
    frames = mtf.get("frames", {})
    values = []

    for item in frames.values():
        close = float(item.get("close", 0) or 0)
        atr_value = float(item.get("atr", 0) or 0)

        if close > 0:
            values.append((atr_value / close) * 100)

    if not values:
        return {"score": 40, "status": "UNKNOWN", "allow": False, "atr_percent": 0}

    avg_vol = sum(values) / len(values)

    if 0.15 <= avg_vol <= 2.5:
        return {
            "score": 85,
            "status": "HEALTHY_VOLATILITY",
            "allow": True,
            "atr_percent": round(avg_vol, 4),
        }

    if avg_vol < 0.15:
        return {
            "score": 45,
            "status": "LOW_VOLATILITY",
            "allow": False,
            "atr_percent": round(avg_vol, 4),
        }

    return {
        "score": 35,
        "status": "HIGH_RISK_VOLATILITY",
        "allow": False,
        "atr_percent": round(avg_vol, 4),
    }


def liquidity_analysis(symbol, volume_24h):
    book = get_best_bid_ask(symbol)

    if not book.get("ok"):
        return {"score": 30, "status": "NO_ORDERBOOK", "allow": False}

    spread = float(book.get("spread_percent", 99) or 99)

    if volume_24h >= 5_000_000 and spread <= 0.15:
        return {"score": 95, "status": "HIGH_LIQUIDITY", "allow": True, "spread_percent": spread}

    if volume_24h >= 500_000 and spread <= 0.35:
        return {"score": 75, "status": "NORMAL_LIQUIDITY", "allow": True, "spread_percent": spread}

    return {"score": 35, "status": "LOW_LIQUIDITY", "allow": False, "spread_percent": spread}


def orderbook_pressure(symbol):
    book = get_best_bid_ask(symbol)

    if not book.get("ok"):
        return {"score": 50, "status": "UNKNOWN", "bias": "NEUTRAL"}

    bid = float(book.get("best_bid", 0) or 0)
    ask = float(book.get("best_ask", 0) or 0)
    spread = float(book.get("spread_percent", 0) or 0)

    if bid <= 0 or ask <= 0:
        return {"score": 50, "status": "UNKNOWN", "bias": "NEUTRAL"}

    mid = (bid + ask) / 2

    if spread <= 0.10:
        return {
            "score": 80,
            "status": "TIGHT_SPREAD",
            "bias": "GOOD_EXECUTION",
            "mid": round(mid, 8),
            "spread_percent": spread,
        }

    if spread <= 0.30:
        return {
            "score": 65,
            "status": "NORMAL_SPREAD",
            "bias": "ACCEPTABLE",
            "mid": round(mid, 8),
            "spread_percent": spread,
        }

    return {
        "score": 35,
        "status": "WIDE_SPREAD",
        "bias": "BAD_EXECUTION",
        "mid": round(mid, 8),
        "spread_percent": spread,
    }


def fee_optimization(symbol):
    book = get_best_bid_ask(symbol)

    if not book.get("ok"):
        return {"score": 40, "allow": False, "required_min_tp": 0.5}

    spread = float(book.get("spread_percent", 0) or 0)

    estimated_roundtrip_fee = 0.20
    safety_buffer = 0.10
    required_min_tp = spread + estimated_roundtrip_fee + safety_buffer

    return {
        "score": 90 if required_min_tp <= 0.45 else 60 if required_min_tp <= 0.7 else 30,
        "allow": required_min_tp <= 0.7,
        "spread_percent": round(spread, 4),
        "estimated_roundtrip_fee": estimated_roundtrip_fee,
        "required_min_tp": round(required_min_tp, 4),
    }


def position_correlation(symbol):
    base = symbol.replace("USDT", "")

    if base in ["BTC", "ETH"]:
        return {"score": 80, "risk": "LOW", "group": "MAJOR"}

    if base in ["ADA", "XRP", "SOL", "WLD"]:
        return {"score": 65, "risk": "MEDIUM", "group": "ALT"}

    return {"score": 50, "risk": "UNKNOWN", "group": "OTHER"}


def learning_score(symbol):
    memory = engine_memory["symbol_scores"].get(symbol)

    if not memory:
        return {"score": 60, "status": "NO_HISTORY"}

    wins = memory.get("wins", 0)
    losses = memory.get("losses", 0)
    total = wins + losses

    if total <= 0:
        return {"score": 60, "status": "NO_HISTORY"}

    winrate = wins / total * 100

    if winrate >= 60:
        return {"score": 85, "status": "GOOD_HISTORY", "winrate": round(winrate, 2)}

    if winrate >= 45:
        return {"score": 60, "status": "NEUTRAL_HISTORY", "winrate": round(winrate, 2)}

    return {"score": 30, "status": "BAD_HISTORY", "winrate": round(winrate, 2)}


def calculate_quantum_score(
    trend,
    volatility,
    liquidity,
    orderbook,
    fee,
    correlation,
    learning,
    change_24h,
    volume_24h,
):
    score = 0

    score += trend["score"] * 0.22
    score += volatility["score"] * 0.15
    score += liquidity["score"] * 0.18
    score += orderbook["score"] * 0.15
    score += fee["score"] * 0.12
    score += correlation["score"] * 0.08
    score += learning["score"] * 0.10

    if 0 < change_24h <= 12:
        score += 5

    if volume_24h >= 1_000_000:
        score += 5

    return round(min(score, 100), 2)


def build_decision(score, trend, volatility, liquidity, orderbook, fee):
    if not trend["allow"]:
        return "WAIT_NO_TREND"

    if not volatility["allow"]:
        return "WAIT_VOLATILITY"

    if not liquidity["allow"]:
        return "WAIT_LIQUIDITY"

    if not fee["allow"]:
        return "WAIT_FEE"

    if score >= 85:
        return "STRONG_LONG"

    if score >= 70:
        return "LONG"

    if score >= 60:
        return "WATCH"

    return "WAIT"


def dynamic_tp_sl(score, volatility, trend):
    atr_percent = float(volatility.get("atr_percent", 0.5) or 0.5)

    if score >= 85 and trend.get("status") == "STRONG_TREND":
        tp = max(0.80, min(2.0, atr_percent * 1.6))
        sl = max(0.35, min(1.0, atr_percent * 0.8))
    elif score >= 70:
        tp = max(0.60, min(1.3, atr_percent * 1.2))
        sl = max(0.35, min(0.8, atr_percent * 0.7))
    else:
        tp = 0.50
        sl = 0.35

    return {
        "tp_percent": round(tp, 3),
        "sl_percent": round(sl, 3),
        "mode": "DYNAMIC",
    }


def portfolio_allocation_v2(balance: float = 100):
    scan = run_quantum_ai_v2_scan(limit=80)
    items = scan["items"]

    strong = [x for x in items if x["decision"] in ["STRONG_LONG", "LONG"]]

    reserve = balance * 0.20
    active = balance - reserve

    allocations = []

    weights = {
        "qe_spot_1": 0.35,
        "qe_spot_2": 0.25,
        "quantum_ai": 0.20,
        "momentum": 0.20,
    }

    top_symbols = strong[:4]

    for index, (bot_id, weight) in enumerate(weights.items()):
        symbol = top_symbols[index]["symbol"] if index < len(top_symbols) else "BTCUSDT"
        ai_item = top_symbols[index] if index < len(top_symbols) else None

        allocations.append(
            {
                "bot_id": bot_id,
                "symbol": symbol,
                "amount": round(active * weight, 2),
                "quantum_score": ai_item["quantum_score"] if ai_item else 70,
                "decision": ai_item["decision"] if ai_item else "WATCH",
                "dynamic_tp_sl": ai_item["dynamic_tp_sl"] if ai_item else {"tp_percent": 0.7, "sl_percent": 0.4},
            }
        )

    return {
        "balance": balance,
        "reserve": round(reserve, 2),
        "active_balance": round(active, 2),
        "allocations": allocations,
        "created_at": now(),
    }


def record_trade_result(symbol, bot_id, pnl):
    pnl = float(pnl or 0)

    engine_memory["trades"].append(
        {
            "symbol": symbol,
            "bot_id": bot_id,
            "pnl": pnl,
            "created_at": now(),
        }
    )

    symbol_memory = engine_memory["symbol_scores"].setdefault(
        symbol,
        {"wins": 0, "losses": 0, "pnl": 0},
    )

    bot_memory = engine_memory["bot_scores"].setdefault(
        bot_id,
        {"wins": 0, "losses": 0, "pnl": 0},
    )

    if pnl > 0:
        symbol_memory["wins"] += 1
        bot_memory["wins"] += 1
    elif pnl < 0:
        symbol_memory["losses"] += 1
        bot_memory["losses"] += 1

    symbol_memory["pnl"] = round(symbol_memory["pnl"] + pnl, 4)
    bot_memory["pnl"] = round(bot_memory["pnl"] + pnl, 4)

    return {
        "message": "Trade result recorded",
        "symbol_memory": symbol_memory,
        "bot_memory": bot_memory,
    }


def get_candles(symbol: str, interval: str, limit: int = 80):
    pair = normalize_pair(symbol)

    try:
        response = requests.get(
            f"{GATEIO_BASE_URL}/spot/candlesticks",
            params={
                "currency_pair": pair,
                "interval": interval,
                "limit": limit,
            },
            timeout=12,
        )

        data = response.json()

        if response.status_code != 200 or not isinstance(data, list):
            return []

        candles = []

        for row in data:
            try:
                candles.append(
                    {
                        "time": float(row[0]),
                        "volume": float(row[1]),
                        "close": float(row[2]),
                        "high": float(row[3]),
                        "low": float(row[4]),
                        "open": float(row[5]),
                    }
                )
            except Exception:
                continue

        candles.sort(key=lambda x: x["time"])
        return candles

    except Exception:
        return []


def ema(values, period):
    if not values:
        return 0

    if len(values) < period:
        return sum(values) / len(values)

    k = 2 / (period + 1)
    result = values[0]

    for price in values[1:]:
        result = price * k + result * (1 - k)

    return result


def rsi(values, period=14):
    if len(values) < period + 1:
        return 50

    gains = []
    losses = []

    for i in range(1, len(values)):
        diff = values[i] - values[i - 1]
        gains.append(max(diff, 0))
        losses.append(abs(min(diff, 0)))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def atr(highs, lows, closes, period=14):
    if len(closes) < period + 1:
        return 0

    trs = []

    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
        trs.append(tr)

    return sum(trs[-period:]) / period


def macd(values):
    if len(values) < 26:
        return {"value": 0, "signal": 0, "histogram": 0}

    ema12 = ema(values, 12)
    ema26 = ema(values, 26)
    value = ema12 - ema26
    signal = value * 0.8
    histogram = value - signal

    return {
        "value": round(value, 8),
        "signal": round(signal, 8),
        "histogram": round(histogram, 8),
        "bias": "BULLISH" if histogram > 0 else "BEARISH",
    }


def normalize_pair(symbol: str):
    clean = symbol.upper().replace("/", "").replace("_", "")

    if clean.endswith("USDT"):
        return clean.replace("USDT", "_USDT")

    return clean


def is_safe_symbol(symbol):
    clean = symbol.upper().replace("/", "").replace("_", "")

    if not clean.endswith("USDT"):
        return False

    for part in BLOCKED_SYMBOL_PARTS:
        if part in clean:
            return False

    return True


def empty_tf(tf):
    return {
        "timeframe": tf,
        "close": 0,
        "ema_fast": 0,
        "ema_slow": 0,
        "rsi": 50,
        "atr": 0,
        "macd": {"value": 0, "signal": 0, "histogram": 0, "bias": "NEUTRAL"},
        "trend": "UNKNOWN",
        "trend_strength": 0,
        "volume_avg": 0,
    }