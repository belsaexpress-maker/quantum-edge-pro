import time
import requests

GATEIO_BASE_URL = "https://api.gateio.ws/api/v4"

_market_cache = {
    "time": 0,
    "data": None,
}

CACHE_SECONDS = 5


def get_market_snapshot(force_refresh: bool = False):
    now = time.time()

    if (
        not force_refresh
        and _market_cache["data"] is not None
        and now - _market_cache["time"] < CACHE_SECONDS
    ):
        return _market_cache["data"]

    crypto = get_gateio_spot_markets()

    data = {
        "exchange": "Gate.io",
        "crypto": crypto,
        "stocks": [],
        "indices": [],
        "commodities": [],
        "forex": [],
    }

    _market_cache["time"] = now
    _market_cache["data"] = data

    return data


def get_gateio_spot_markets():
    try:
        response = requests.get(
            f"{GATEIO_BASE_URL}/spot/tickers",
            timeout=20,
        )

        data = response.json()

        if response.status_code != 200 or not isinstance(data, list):
            return []

        items = []

        for item in data:
            pair = item.get("currency_pair", "")

            if not pair.endswith("_USDT"):
                continue

            symbol = pair.replace("_", "")
            price = safe_float(item.get("last"))

            if price <= 0:
                continue

            change = safe_float(item.get("change_percentage"))
            quote_volume = safe_float(item.get("quote_volume"))
            base_volume = safe_float(item.get("base_volume"))
            high_24h = safe_float(item.get("high_24h"))
            low_24h = safe_float(item.get("low_24h"))

            items.append(
                {
                    "symbol": symbol,
                    "name": symbol.replace("USDT", "/USDT"),
                    "asset_type": "crypto",
                    "exchange": "Gate.io",
                    "price": price,
                    "change_24h": change,
                    "volume_24h": quote_volume,
                    "base_volume": base_volume,
                    "high_24h": high_24h,
                    "low_24h": low_24h,
                    "signal": build_signal(change, quote_volume),
                    "source": "Gate.io Live",
                }
            )

        items.sort(key=lambda x: x["volume_24h"], reverse=True)
        return items

    except Exception as error:
        print("Gate.io market error:", error)
        return []


def safe_float(value):
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def build_signal(change_24h, volume_24h):
    if volume_24h <= 0:
        return "NO DATA"

    if change_24h >= 5:
        return "STRONG BUY 🟢"

    if change_24h >= 1:
        return "BUY 🟢"

    if change_24h <= -5:
        return "STRONG SELL 🔴"

    if change_24h <= -1:
        return "SELL 🔴"

    return "WATCH ⚪"