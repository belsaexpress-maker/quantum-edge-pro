import requests

BINANCE_BASE_URLS = [
    "https://api.binance.com",
    "https://api1.binance.com",
    "https://api2.binance.com",
    "https://api3.binance.com",
]


def request_binance(path: str):
    for base_url in BINANCE_BASE_URLS:
        try:
            response = requests.get(f"{base_url}{path}", timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception:
            continue

    return None


def get_binance_usdt_markets(limit: int = 300):
    tickers = request_binance("/api/v3/ticker/24hr")

    if not tickers:
        return fallback_crypto_markets()

    results = []

    for item in tickers:
        symbol = item.get("symbol", "")

        if not symbol.endswith("USDT"):
            continue

        price = float(item.get("lastPrice", 0) or 0)
        change = float(item.get("priceChangePercent", 0) or 0)
        volume = float(item.get("quoteVolume", 0) or 0)

        if price <= 0:
            continue

        results.append(
            {
                "symbol": symbol,
                "name": symbol.replace("USDT", "/USDT"),
                "asset_type": "crypto",
                "exchange": "Binance",
                "price": price,
                "change_24h": round(change, 2),
                "volume_24h": round(volume, 2),
                "signal": generate_signal(change),
            }
        )

    results = sorted(
        results,
        key=lambda item: item["volume_24h"],
        reverse=True,
    )

    return results[:limit]


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


def fallback_crypto_markets():
    symbols = [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
        "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "TRXUSDT", "DOTUSDT",
        "LINKUSDT", "LTCUSDT", "BCHUSDT", "ATOMUSDT", "UNIUSDT",
        "APTUSDT", "ARBUSDT", "OPUSDT", "NEARUSDT", "INJUSDT",
        "SUIUSDT", "SEIUSDT", "PEPEUSDT", "WIFUSDT", "FETUSDT",
    ]

    return [
        {
            "symbol": symbol,
            "name": symbol.replace("USDT", "/USDT"),
            "asset_type": "crypto",
            "exchange": "Binance / Fallback",
            "price": 0,
            "change_24h": 0,
            "volume_24h": 0,
            "signal": "NO LIVE DATA ⚪",
        }
        for symbol in symbols
    ]