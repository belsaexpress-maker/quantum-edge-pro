import requests


GATEIO_TICKERS_URL = "https://api.gateio.ws/api/v4/spot/tickers"


def fetch_gateio_spot_tickers():
    try:
        response = requests.get(GATEIO_TICKERS_URL, timeout=12)

        if response.status_code != 200:
            return []

        data = response.json()
        results = []

        for item in data:
            pair = item.get("currency_pair", "")

            if not pair.endswith("_USDT"):
                continue

            symbol = pair.replace("_", "")
            price = float(item.get("last", 0) or 0)
            change = float(item.get("change_percentage", 0) or 0)
            volume = float(item.get("quote_volume", 0) or 0)

            results.append(
                {
                    "symbol": symbol,
                    "name": pair.replace("_", "/"),
                    "asset_type": "crypto",
                    "exchange": "Gate.io",
                    "price": price,
                    "change_24h": round(change, 2),
                    "volume_24h": round(volume, 2),
                    "signal": generate_signal(change),
                }
            )

        return sorted(results, key=lambda x: x["volume_24h"], reverse=True)

    except Exception:
        return []


def generate_signal(change: float):
    if change >= 5:
        return "STRONG BUY 🚀"
    if change >= 2:
        return "BUY 🟢"
    if change <= -5:
        return "STRONG SELL 🔴"
    if change <= -2:
        return "SELL 🔴"
    return "HOLD ⚪"