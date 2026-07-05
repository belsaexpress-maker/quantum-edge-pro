from app.ai.scanner_engine import get_scanner_results, scan_all_market
from app.ai.smart_money_engine import analyze_smart_money


def generate_playbook(symbol: str = "BTCUSDT", timeframe: str = "1h"):
    symbol = symbol.upper()

    scan_all_market()
    scanner_items = get_scanner_results(1000).get("items", [])

    item = next((x for x in scanner_items if x.get("symbol") == symbol), None)

    if not item:
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "error": "Scanner içinde coin bulunamadı",
        }

    smc = analyze_smart_money(symbol)

    price = float(item.get("price", 0) or 0)
    ai_score = int(item.get("confidence", 0) or 0)
    smc_score = int(smc.get("smart_money_score", 0) or 0)

    if price <= 0:
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "error": "Fiyat bulunamadı",
        }

    signal = get_signal(ai_score, smc_score)

    entry_low = round(price * 0.996, 8)
    entry_high = round(price * 1.002, 8)
    stop_loss = round(price * 0.985, 8)

    tp1 = round(price * 1.006, 8)
    tp2 = round(price * 1.012, 8)
    tp3 = round(price * 1.025, 8)

    risk = abs(price - stop_loss)
    reward = abs(tp2 - price)
    rr = round(reward / risk, 2) if risk > 0 else 0

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "price": price,
        "signal": signal,
        "ai_score": ai_score,
        "smart_money_score": smc_score,
        "entry_zone": {
            "low": entry_low,
            "high": entry_high,
        },
        "stop_loss": stop_loss,
        "take_profit": {
            "tp1": tp1,
            "tp2": tp2,
            "tp3": tp3,
        },
        "risk_reward": rr,
        "confidence": round((ai_score + smc_score) / 2),
        "reasons": [
            f"AI Score: {ai_score}/100",
            f"Smart Money Score: {smc_score}/100",
            f"Direction: {item.get('direction')}",
            f"24h Change: {item.get('change_24h')}%",
            f"Volume: {item.get('volume_24h')}",
            f"Risk/Reward: {rr}",
        ],
        "smart_money": smc,
    }


def generate_ai_playbook(symbol: str = "BTCUSDT", timeframe: str = "1h"):
    return generate_playbook(symbol, timeframe)


def get_signal(ai_score: int, smc_score: int):
    total = round((ai_score + smc_score) / 2)

    if total >= 85:
        return "STRONG LONG"

    if total >= 70:
        return "LONG"

    if total >= 55:
        return "WATCH"

    if total <= 35:
        return "SHORT WATCH"

    return "WAIT"