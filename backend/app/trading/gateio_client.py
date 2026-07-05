import hashlib
import hmac
import json
import os
import time
from pathlib import Path
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH, override=True)

GATEIO_LIVE_HOST = "https://api.gateio.ws"
GATEIO_TESTNET_HOST = "https://api-testnet.gateapi.io"
API_PREFIX = "/api/v4"

DEFAULT_SLIPPAGE_PERCENT = 0.15


def get_trading_mode():
    return os.getenv("TRADING_MODE", "PAPER").upper()


def get_host():
    mode = get_trading_mode()

    if mode == "TESTNET":
        return GATEIO_TESTNET_HOST

    return GATEIO_LIVE_HOST


def get_keys():
    api_key = os.getenv("GATEIO_API_KEY", "").strip()
    api_secret = os.getenv("GATEIO_API_SECRET", "").strip()

    return api_key, api_secret


def keys_are_ready():
    api_key, api_secret = get_keys()
    return bool(api_key and api_secret)


def normalize_spot_pair(symbol: str):
    clean = symbol.upper().replace("/", "").replace("_", "")

    if clean.endswith("USDT"):
        return clean.replace("USDT", "_USDT")

    return clean


def gen_sign(method: str, request_path: str, query_string: str = "", body_string: str = ""):
    api_key, api_secret = get_keys()

    timestamp = str(int(time.time()))
    body_hash = hashlib.sha512(body_string.encode("utf-8")).hexdigest()

    sign_string = "\n".join(
        [
            method.upper(),
            request_path,
            query_string,
            body_hash,
            timestamp,
        ]
    )

    signature = hmac.new(
        api_secret.encode("utf-8"),
        sign_string.encode("utf-8"),
        hashlib.sha512,
    ).hexdigest()

    return {
        "KEY": api_key,
        "Timestamp": timestamp,
        "SIGN": signature,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def public_gateio_request(path: str, params=None):
    params = params or {}
    query_string = urlencode(params)
    request_path = f"{API_PREFIX}{path}"

    url = f"{get_host()}{request_path}"

    if query_string:
        url = f"{url}?{query_string}"

    try:
        response = requests.get(url, timeout=10)

        try:
            data = response.json()
        except Exception:
            data = {"raw": response.text}

        return {
            "ok": 200 <= response.status_code < 300,
            "mode": get_trading_mode(),
            "host": get_host(),
            "method": "GET",
            "path": request_path,
            "status_code": response.status_code,
            "data": data,
        }

    except Exception as error:
        return {
            "ok": False,
            "mode": get_trading_mode(),
            "host": get_host(),
            "method": "GET",
            "path": request_path,
            "status_code": None,
            "error": str(error),
            "data": None,
        }


def gateio_request(method: str, path: str, params=None, body=None):
    mode = get_trading_mode()

    if mode == "PAPER":
        return {
            "ok": False,
            "mode": mode,
            "error": "PAPER modda Gate.io API istegi gonderilmez.",
            "status_code": None,
            "data": None,
        }

    if mode == "LIVE":
        return {
            "ok": False,
            "mode": mode,
            "error": "LIVE islem guvenlik icin kapali.",
            "status_code": None,
            "data": None,
        }

    if not keys_are_ready():
        return {
            "ok": False,
            "mode": mode,
            "error": "Gate.io API key veya secret eksik.",
            "env_path": str(ENV_PATH),
            "status_code": None,
            "data": None,
        }

    params = params or {}
    body = body or {}

    query_string = urlencode(params)
    body_string = json.dumps(body, separators=(",", ":")) if body else ""

    request_path = f"{API_PREFIX}{path}"

    headers = gen_sign(
        method=method,
        request_path=request_path,
        query_string=query_string,
        body_string=body_string,
    )

    url = f"{get_host()}{request_path}"

    if query_string:
        url = f"{url}?{query_string}"

    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            data=body_string if body else None,
            timeout=15,
        )

        try:
            data = response.json()
        except Exception:
            data = {"raw": response.text}

        return {
            "ok": 200 <= response.status_code < 300,
            "mode": mode,
            "host": get_host(),
            "method": method.upper(),
            "path": request_path,
            "status_code": response.status_code,
            "data": data,
        }

    except Exception as error:
        return {
            "ok": False,
            "mode": mode,
            "host": get_host(),
            "method": method.upper(),
            "path": f"{API_PREFIX}{path}",
            "status_code": None,
            "error": str(error),
            "data": None,
        }


def get_spot_accounts():
    return gateio_request("GET", "/spot/accounts")


def get_orderbook(symbol: str, limit: int = 5):
    pair = normalize_spot_pair(symbol)

    return public_gateio_request(
        "/spot/order_book",
        params={
            "currency_pair": pair,
            "limit": limit,
            "with_id": "true",
        },
    )


def get_best_bid_ask(symbol: str):
    orderbook = get_orderbook(symbol, limit=5)

    if not orderbook.get("ok"):
        return {
            "ok": False,
            "symbol": symbol.upper(),
            "error": "Orderbook okunamadi",
            "orderbook_response": orderbook,
        }

    data = orderbook.get("data") or {}
    bids = data.get("bids") or []
    asks = data.get("asks") or []

    if not bids or not asks:
        return {
            "ok": False,
            "symbol": symbol.upper(),
            "error": "Orderbook bos geldi",
            "orderbook_response": orderbook,
        }

    try:
        best_bid = float(bids[0][0])
        best_ask = float(asks[0][0])
    except Exception:
        return {
            "ok": False,
            "symbol": symbol.upper(),
            "error": "Best bid/ask okunamadi",
            "orderbook_response": orderbook,
        }

    return {
        "ok": True,
        "symbol": symbol.upper(),
        "best_bid": best_bid,
        "best_ask": best_ask,
        "spread": round(best_ask - best_bid, 8),
        "spread_percent": round(((best_ask - best_bid) / best_bid) * 100, 4) if best_bid > 0 else 0,
        "orderbook_response": orderbook,
    }


def build_ioc_price(symbol: str, side: str, fallback_price: str | float | None = None):
    side = side.lower()
    book = get_best_bid_ask(symbol)

    if not book.get("ok"):
        if fallback_price is None:
            return {
                "ok": False,
                "error": "Orderbook yok ve fallback price yok",
                "book": book,
            }

        return {
            "ok": True,
            "price": float(fallback_price),
            "source": "fallback_price",
            "book": book,
        }

    slippage = DEFAULT_SLIPPAGE_PERCENT / 100

    if side == "buy":
        price = book["best_ask"] * (1 + slippage)
    else:
        price = book["best_bid"] * (1 - slippage)

    return {
        "ok": True,
        "price": round(price, 8),
        "source": "orderbook_slippage",
        "side": side,
        "best_bid": book["best_bid"],
        "best_ask": book["best_ask"],
        "spread": book["spread"],
        "spread_percent": book["spread_percent"],
    }


def create_spot_order(symbol: str, side: str, amount: str, price: str | None = None):
    mode = get_trading_mode()

    if mode == "LIVE":
        return {
            "ok": False,
            "mode": mode,
            "error": "LIVE emir gonderimi kapali.",
        }

    pair = normalize_spot_pair(symbol)
    side = side.lower()

    ioc_price_result = build_ioc_price(
        symbol=symbol,
        side=side,
        fallback_price=price,
    )

    if not ioc_price_result.get("ok"):
        return {
            "ok": False,
            "mode": mode,
            "symbol": symbol.upper(),
            "currency_pair": pair,
            "side": side,
            "error": "IOC fiyat hesaplanamadi",
            "price_result": ioc_price_result,
        }

    final_price = ioc_price_result["price"]

    order = {
        "currency_pair": pair,
        "side": side,
        "amount": str(amount),
        "account": "spot",
        "type": "limit",
        "price": str(final_price),
        "time_in_force": "ioc",
    }

    result = gateio_request("POST", "/spot/orders", body=order)

    return {
        "ok": result.get("ok", False),
        "mode": mode,
        "symbol": symbol.upper(),
        "currency_pair": pair,
        "side": side,
        "amount": str(amount),
        "requested_price": str(price) if price else None,
        "final_price": str(final_price),
        "price_source": ioc_price_result,
        "order_type": order["type"],
        "time_in_force": order["time_in_force"],
        "request_order": order,
        "exchange_response": result,
    }


def get_spot_order(order_id: str, symbol: str):
    pair = normalize_spot_pair(symbol)

    return gateio_request(
        "GET",
        f"/spot/orders/{order_id}",
        params={
            "currency_pair": pair,
            "account": "spot",
        },
    )


def get_open_orders(symbol: str | None = None):
    params = {
        "account": "spot",
    }

    if symbol:
        params["currency_pair"] = normalize_spot_pair(symbol)

    return gateio_request(
        "GET",
        "/spot/open_orders",
        params=params,
    )


def cancel_open_orders(symbol: str):
    pair = normalize_spot_pair(symbol)

    return gateio_request(
        "DELETE",
        "/spot/orders",
        params={
            "currency_pair": pair,
            "account": "spot",
        },
    )


def cancel_many_open_orders(symbols: list[str]):
    results = []

    for symbol in symbols:
        results.append(
            {
                "symbol": symbol.upper(),
                "result": cancel_open_orders(symbol),
            }
        )

    return {
        "mode": get_trading_mode(),
        "count": len(results),
        "results": results,
    }