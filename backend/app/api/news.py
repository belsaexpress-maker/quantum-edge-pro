from datetime import datetime
from fastapi import APIRouter

router = APIRouter(prefix="/news", tags=["News"])


@router.get("/latest")
def latest_news():
    return [
        {
            "title": "Quantum Edge market engine active",
            "source": "System",
            "summary": "Gate.io canlı piyasa verileri aktif.",
            "url": "#",
            "published_at": datetime.utcnow().isoformat(),
        },
        {
            "title": "AI Scanner and Playbook active",
            "source": "System",
            "summary": "AI Scanner, Opportunities, Smart Money ve Playbook motorları aktif.",
            "url": "#",
            "published_at": datetime.utcnow().isoformat(),
        },
    ]