import requests


def get_market_data():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"

        params = {
            "ids": "bitcoin,ethereum,solana",
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if "status" in data:
            return fallback_market_data()

        return data

    except Exception:
        return fallback_market_data()


def fallback_market_data():
    return {
        "bitcoin": {
            "usd": 0,
            "usd_24h_change": 0
        },
        "ethereum": {
            "usd": 0,
            "usd_24h_change": 0
        },
        "solana": {
            "usd": 0,
            "usd_24h_change": 0
        }
    }