from fastapi import APIRouter

from app.ai.scanner_engine import scan_all_market, get_scanner_results

router = APIRouter(prefix="/scanner", tags=["AI Scanner"])


@router.get("/")
def scanner_home(limit: int = 100):
    return get_scanner_results(limit)


@router.get("/refresh")
def refresh_scanner():
    return scan_all_market()


@router.get("/top")
def scanner_top(limit: int = 50):
    return get_scanner_results(limit)