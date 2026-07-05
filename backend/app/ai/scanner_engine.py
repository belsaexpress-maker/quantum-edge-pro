from datetime import datetime

from app.market_engine.market_manager import get_market_snapshot

scanner_state = {
    "last_scan": None,
    "items": [],
}


def scan_all_market():
    snapshot = get_market_snapshot(force_refresh=True)
    coins = snapshot.get("crypto", [])

    results = []

    for coin in coins:
        price = float(coin.get("price", 0) or 0)
        change = float(coin.get("change_24h", 0) or 0)
        volume = float(coin.get("volume_24h", 0) or 0)

        if price <= 0:
            continue

        confidence = calculate_confidence(change, volume)
        direction = calculate_direction(change, confidence)

        results.append(
            {
                "symbol": coin.get("symbol"),
                "name": coin.get("name"),
                "price": price,
                "change_24h": change,
                "volume_24h": volume,
                "confidence": confidence,
                "direction": direction,
                "signal": coin.get("signal", "WATCH"),
                "source": coin.get("source", "Gate.io Live"),
                "updated_at": datetime.utcnow().isoformat(),
            }
        )

    results.sort(key=lambda x: x["confidence"], reverse=True)

    scanner_state["items"] = results
    scanner_state["last_scan"] = datetime.utcnow().isoformat()

    return {
        "count": len(results),
        "last_scan": scanner_state["last_scan"],
        "items": results,
    }


def get_scanner_results(limit: int = 100):
    if not scanner_state["items"]:
        scan_all_market()

    return {
        "count": len(scanner_state["items"][:limit]),
        "last_scan": scanner_state["last_scan"],
        "items": scanner_state["items"][:limit],
    }


def calculate_confidence(change_24h: float, volume_24h: float):
    score = 50

    if change_24h >= 10:
        score += 25
    elif change_24h >= 5:
        score += 18
    elif change_24h >= 1:
        score += 10
    elif change_24h <= -10:
        score -= 25
    elif change_24h <= -5:
        score -= 18
    elif change_24h <= -1:
        score -= 10

    if volume_24h >= 10_000_000:
        score += 20
    elif volume_24h >= 1_000_000:
        score += 12
    elif volume_24h >= 100_000:
        score += 6

    return max(1, min(100, round(score)))


def calculate_direction(change_24h: float, confidence: int):
    if confidence >= 70 and change_24h > 0:
        return "LONG"

    if confidence <= 35 and change_24h < 0:
        return "SHORT"

    return "WAIT"