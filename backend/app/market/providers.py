import requests

from app.market.signals import generate_market_signal


def _fallback():
    return {
        "crypto": [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "asset_type": "crypto",
                "price": 0,
                "change_24h": 0,
                "signal": "HOLD ⚪",
            },
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "asset_type": "crypto",
                "price": 0,
                "change_24h": 0,
                "signal": "HOLD ⚪",
            },
            {
                "symbol": "SOL",
                "name": "Solana",
                "asset_type": "crypto",
                "price": 0,
                "change_24h": 0,
                "signal": "HOLD ⚪",
            },
        ],
        "stocks": [
            {"symbol": "AAPL", "name": "Apple", "asset_type": "stock", "price": 0, "change_24h": 0, "signal": "WATCH"},
            {"symbol": "NVDA", "name": "Nvidia", "asset_type": "stock", "price": 0, "change_24h": 0, "signal": "WATCH"},
            {"symbol": "TSLA", "name": "Tesla", "asset_type": "stock", "price": 0, "change_24h": 0, "signal": "WATCH"},
        ],
        "indices": [
            {"symbol": "SPX", "name": "S&P 500", "asset_type": "index", "price": 0, "change_24h": 0, "signal": "WATCH"},
            {"symbol": "NDX", "name": "Nasdaq 100", "asset_type": "index", "price": 0, "change_24h": 0, "signal": "WATCH"},
            {"symbol": "XU100", "name": "BIST 100", "asset_type": "index", "price": 0, "change_24h": 0, "signal": "WATCH"},
        ],
        "commodities": [
            {"symbol": "XAUUSD", "name": "Gold", "asset_type": "commodity", "price": 0, "change_24h": 0, "signal": "WATCH"},
            {"symbol": "XAGUSD", "name": "Silver", "asset_type": "commodity", "price": 0, "change_24h": 0, "signal": "WATCH"},
            {"symbol": "BRENT", "name": "Brent Oil", "asset_type": "commodity", "price": 0, "change_24h": 0, "signal": "WATCH"},
        ],
        "forex": [
            {"symbol": "EURUSD", "name": "EUR/USD", "asset_type": "forex", "price": 0, "change_24h": 0, "signal": "WATCH"},
            {"symbol": "USDTRY", "name": "USD/TRY", "asset_type": "forex", "price": 0, "change_24h": 0, "signal": "WATCH"},
            {"symbol": "GBPUSD", "name": "GBP/USD", "asset_type": "forex", "price": 0, "change_24h": 0, "signal": "WATCH"},
        ],
    }


def get_global_market_snapshot():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,solana",
            "vs_currencies": "usd",
            "include_24hr_change": "true",
        }

        response = requests.get(url, params=params, timeout=8)
        data = response.json()

        if "status" in data:
            return _fallback()

        crypto = []

        mapping = [
            ("bitcoin", "BTC", "Bitcoin"),
            ("ethereum", "ETH", "Ethereum"),
            ("solana", "SOL", "Solana"),
        ]

        for key, symbol, name in mapping:
            item = data.get(key, {})
            price = float(item.get("usd", 0))
            change = float(item.get("usd_24h_change", 0))

            crypto.append(
                {
                    "symbol": symbol,
                    "name": name,
                    "asset_type": "crypto",
                    "price": round(price, 4),
                    "change_24h": round(change, 2),
                    "signal": generate_market_signal(change),
                }
            )

        result = _fallback()
        result["crypto"] = crypto

        return result

    except Exception:
        return _fallback()