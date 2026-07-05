from app.ai.scanner_engine import get_scanner_results, scan_all_market
from app.ai.smart_money_engine import analyze_smart_money


def scan_opportunities(limit: int = 100):
    scan_all_market()
    scanner = get_scanner_results(500).get("items", [])

    results = []

    for item in scanner:
        symbol = item.get("symbol")
        if not symbol:
            continue

        ai_score = int(item.get("confidence", 0) or 0)
        change_24h = float(item.get("change_24h", 0) or 0)
        volume_24h = float(item.get("volume_24h", 0) or 0)
        direction = item.get("direction", "WAIT")

        smc = analyze_smart_money(symbol)
        smc_score = int(smc.get("smart_money_score", 0) or 0)

        opportunity_score = calculate_opportunity_score(
            ai_score=ai_score,
            smc_score=smc_score,
            change_24h=change_24h,
            volume_24h=volume_24h,
            direction=direction,
        )

        decision = get_decision(opportunity_score, direction)

        results.append(
            {
                "symbol": symbol,
                "price": item.get("price", 0),
                "ai_score": ai_score,
                "smart_money_score": smc_score,
                "opportunity_score": opportunity_score,
                "direction": direction,
                "decision": decision,
                "change_24h": change_24h,
                "volume_24h": volume_24h,
                "market_structure": smc.get("market_structure"),
                "order_block": smc.get("order_block"),
                "liquidity": smc.get("liquidity"),
                "reasons": build_reasons(
                    ai_score,
                    smc_score,
                    opportunity_score,
                    direction,
                    change_24h,
                    volume_24h,
                ),
            }
        )

    results.sort(key=lambda x: x["opportunity_score"], reverse=True)

    return {
        "count": len(results[:limit]),
        "items": results[:limit],
        "best_long": next((x for x in results if x["decision"] in ["STRONG_LONG", "LONG"]), None),
        "best_short": next((x for x in results if x["decision"] in ["STRONG_SHORT", "SHORT"]), None),
    }


def calculate_opportunity_score(ai_score, smc_score, change_24h, volume_24h, direction):
    score = 0

    score += ai_score * 0.45
    score += smc_score * 0.30

    if direction == "LONG":
        score += 10
    elif direction == "SHORT":
        score += 7

    if volume_24h > 5_000_000:
        score += 10
    elif volume_24h > 1_000_000:
        score += 6
    elif volume_24h > 300_000:
        score += 3

    if 0.5 <= change_24h <= 8:
        score += 7
    elif -5 <= change_24h < 0:
        score += 3
    elif change_24h > 15:
        score -= 8

    return round(max(1, min(100, score)))


def get_decision(score, direction):
    if score >= 90 and direction == "LONG":
        return "STRONG_LONG"

    if score >= 75 and direction in ["LONG", "WAIT"]:
        return "LONG"

    if score >= 65:
        return "WATCH"

    if score <= 30 and direction == "SHORT":
        return "STRONG_SHORT"

    if score <= 40:
        return "SHORT"

    return "WAIT"


def build_reasons(ai_score, smc_score, opportunity_score, direction, change_24h, volume_24h):
    return [
        f"AI Score: {ai_score}/100",
        f"Smart Money Score: {smc_score}/100",
        f"Opportunity Score: {opportunity_score}/100",
        f"Direction: {direction}",
        f"24h Change: {change_24h}%",
        f"Volume: {volume_24h}",
    ]