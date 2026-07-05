import requests
from fastapi import APIRouter

router = APIRouter(prefix="/orderbook", tags=["Order Book"])

GATEIO_BASE_URL = "https://api.gateio.ws/api/v4"


@router.get("/{symbol}")
def get_orderbook(symbol: str, limit: int = 20):
    pair = symbol.upper().replace("USDT", "_USDT")

    try:
        response = requests.get(
            f"{GATEIO_BASE_URL}/spot/order_book",
            params={
                "currency_pair": pair,
                "limit": limit,
                "with_id": "true",
            },
            timeout=10,
        )

        data = response.json()

        if response.status_code != 200:
            return {
                "symbol": symbol.upper(),
                "error": data,
                "bids": [],
                "asks": [],
            }

        bids = [
            {
                "price": float(item[0]),
                "quantity": float(item[1]),
                "total": round(float(item[0]) * float(item[1]), 2),
            }
            for item in data.get("bids", [])
        ]

        asks = [
            {
                "price": float(item[0]),
                "quantity": float(item[1]),
                "total": round(float(item[0]) * float(item[1]), 2),
            }
            for item in data.get("asks", [])
        ]

        return {
            "symbol": symbol.upper(),
            "pair": pair,
            "bids": bids,
            "asks": asks,
        }

    except Exception as error:
        return {
            "symbol": symbol.upper(),
            "error": str(error),
            "bids": [],
            "asks": [],
        }