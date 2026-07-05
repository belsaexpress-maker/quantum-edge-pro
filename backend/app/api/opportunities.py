from fastapi import APIRouter

from app.ai.opportunity_engine import scan_opportunities

router = APIRouter(prefix="/opportunities", tags=["Quantum Opportunities"])


@router.get("/")
def opportunities(limit: int = 100):
    return scan_opportunities(limit)