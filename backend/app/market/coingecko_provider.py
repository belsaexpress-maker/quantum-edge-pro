import requests


COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"


def get_coingecko_markets(limit: int = 250):
    try:
        response = requests.get(
            COINGECKO_URL,
            params={
                "vs_currency": "usd",
                "order": "volume_desc",
                "per_page": limit,
                "page": 1,
                "sparkline": "false",
                "price_change_percentage": "24h",
            },
            timeout=10,
        )

        if response.status_code != 200:
            return []

        data = response.json()
        results = []

        for item in data:
            symbol = str(item.get("symbol", "")).upper()
            name = item.get("name", symbol)
            price = float(item.get("current_price") or 0)
            change = float(item.get("price_change_percentage_24h") or 0)
            volume = float(item.get("total_volume") or 0)

            results.append(
                {
                    "symbol": f"{symbol}USDT",
                    "name": name,
                    "asset_type": "crypto",
                    "exchange": "CoinGecko",
                    "price": price,
                    "change_24h": round(change, 2),
                    "volume_24h": round(volume, 2),
                    "signal": generate_signal(change),
                }
            )

        return results

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