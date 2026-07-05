from fastapi import APIRouter, HTTPException

from app.market_engine.market_manager import get_market_snapshot

router = APIRouter(prefix="/market", tags=["Market"])


@router.get("/")
def market_root():
    return {
        "status": "ONLINE",
        "exchange": "Gate.io",
        "message": "Quantum Edge Market API",
    }


@router.get("/overview")
def market_overview(force_refresh: bool = False):
    return get_market_snapshot(force_refresh=force_refresh)


@router.get("/coins")
def market_coins(force_refresh: bool = False):
    snapshot = get_market_snapshot(force_refresh=force_refresh)
    return snapshot.get("crypto", [])


@router.get("/coin/{symbol}")
def market_coin(symbol: str):
    snapshot = get_market_snapshot()

    symbol = symbol.upper()

    for coin in snapshot.get("crypto", []):
        if coin["symbol"] == symbol:
            return coin

    raise HTTPException(
        status_code=404,
        detail=f"{symbol} bulunamadı",
    )


@router.get("/refresh")
def refresh_market():
    return get_market_snapshot(force_refresh=True)