from app.market_engine.market_manager import get_market_snapshot


def analyze_smart_money(symbol: str):
    symbol = symbol.upper()
    price = find_price(symbol)

    if price <= 0:
        return {"error": "Canlı fiyat bulunamadı"}

    support = round(price * 0.985, 8)
    resistance = round(price * 1.018, 8)

    order_block_low = round(price * 0.992, 8)
    order_block_high = round(price * 0.998, 8)

    fvg_low = round(price * 1.004, 8)
    fvg_high = round(price * 1.012, 8)

    liquidity_low = round(price * 0.975, 8)
    liquidity_high = round(price * 1.025, 8)

    premium_zone = round(price * 1.015, 8)
    discount_zone = round(price * 0.985, 8)

    score = 50

    if price > support:
        score += 10

    if price < resistance:
        score += 10

    if order_block_low <= price <= order_block_high:
        score += 20

    if price < premium_zone:
        score += 10

    if price > discount_zone:
        score += 10

    score = max(1, min(100, score))

    return {
        "symbol": symbol,
        "price": price,
        "smart_money_score": score,
        "market_structure": "BULLISH" if score >= 70 else "NEUTRAL",
        "order_block": {
            "low": order_block_low,
            "high": order_block_high,
            "status": "ACTIVE" if order_block_low <= price <= order_block_high else "WAITING",
        },
        "fair_value_gap": {
            "low": fvg_low,
            "high": fvg_high,
            "status": "ABOVE_PRICE" if fvg_low > price else "FILLED",
        },
        "liquidity": {
            "buy_side": liquidity_high,
            "sell_side": liquidity_low,
        },
        "bos": score >= 75,
        "choch": score < 45,
        "premium_zone": premium_zone,
        "discount_zone": discount_zone,
        "support": support,
        "resistance": resistance,
        "decision": get_decision(score),
    }


def get_decision(score: int):
    if score >= 80:
        return "STRONG LONG"
    if score >= 65:
        return "LONG WATCH"
    if score <= 35:
        return "SHORT WATCH"
    return "WAIT"


def find_price(symbol: str):
    snapshot = get_market_snapshot()
    coins = snapshot.get("crypto", [])

    item = next((coin for coin in coins if coin.get("symbol") == symbol), None)

    if not item:
        return 0

    return float(item.get("price", 0) or 0)