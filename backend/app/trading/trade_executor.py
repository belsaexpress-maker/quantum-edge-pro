import os
from pathlib import Path

from dotenv import load_dotenv

from app.ai.paper_trading_engine import create_paper_order
from app.trading.gateio_client import create_spot_order, get_spot_accounts


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)


def get_trading_mode():
    return os.getenv("TRADING_MODE", "PAPER").upper()


def get_trading_status():
    mode = get_trading_mode()

    return {
        "mode": mode,
        "paper": mode == "PAPER",
        "testnet": mode == "TESTNET",
        "live": mode == "LIVE",
        "live_enabled": False,
        "env_path": str(ENV_PATH),
        "message": "LIVE güvenlik için kapalı. TESTNET veya PAPER kullan.",
    }


def execute_trade(symbol: str, side: str, price: float, quantity: float):
    mode = get_trading_mode()

    if mode == "PAPER":
        return create_paper_order(
            symbol=symbol,
            side=side,
            price=price,
            quantity=quantity,
        )

    if mode == "TESTNET":
        result = create_spot_order(
            symbol=symbol,
            side=side,
            amount=str(quantity),
            price=str(price),
        )

        return {
            "message": "Gate.io TESTNET order request sent",
            "mode": "TESTNET",
            "symbol": symbol,
            "side": side,
            "price": price,
            "quantity": quantity,
            "exchange_response": result,
        }

    if mode == "LIVE":
        return {
            "error": "LIVE işlem kapalı. Güvenlik onayı olmadan açılmayacak.",
            "mode": "LIVE",
        }

    return {"error": "Geçersiz trading mode"}


def test_exchange_connection():
    mode = get_trading_mode()

    if mode == "PAPER":
        return {
            "mode": "PAPER",
            "message": "Paper mode aktif. Borsa bağlantısı gerekmez.",
        }

    result = get_spot_accounts()

    return {
        "mode": mode,
        "message": "Exchange connection tested",
        "exchange_response": result,
    }