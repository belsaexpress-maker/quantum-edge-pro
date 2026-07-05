import hashlib
import hmac
import json
import os
import time
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=True)

GATEIO_LIVE_HOST = "https://api.gateio.ws"
GATEIO_TESTNET_HOST = "https://api-testnet.gateapi.io"
API_PREFIX = "/api/v4"


def get_host():
    mode = os.getenv("TRADING_MODE", "PAPER").upper()
    return GATEIO_TESTNET_HOST if mode == "TESTNET" else GATEIO_LIVE_HOST


def get_keys():
    return (
        os.getenv("GATEIO_API_KEY", "").strip(),
        os.getenv("GATEIO_API_SECRET", "").strip(),
    )


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


def gateio_request(method: str, path: str, params=None, body=None):
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
        "status_code": response.status_code,
        "data": data,
    }


def get_spot_accounts():
    return gateio_request("GET", "/spot/accounts")


def create_spot_order(symbol: str, side: str, amount: str, price: str | None = None):
    pair = symbol.upper().replace("USDT", "_USDT")

    order = {
        "currency_pair": pair,
        "side": side.lower(),
        "amount": amount,
        "account": "spot",
    }

    if price:
        order["type"] = "limit"
        order["price"] = price
    else:
        order["type"] = "market"

    return gateio_request("POST", "/spot/orders", body=order)