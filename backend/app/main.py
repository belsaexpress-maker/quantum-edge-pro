from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings
from app.database.base import Base
from app.database.database import engine

from app.models.user import User
from app.models.portfolio import PortfolioAsset
from app.models.watchlist import WatchlistItem
from app.models.alert import PriceAlert

from app.api.auth import router as auth_router
from app.api.market import router as market_router
from app.api.news import router as news_router
from app.api.portfolio import router as portfolio_router
from app.api.watchlist import router as watchlist_router
from app.api.ai import router as ai_router
from app.api.playbook import router as playbook_router
from app.api.scanner import router as scanner_router
from app.api.intelligence import router as intelligence_router
from app.api.opportunities import router as opportunities_router
from app.api.orderbook import router as orderbook_router
from app.api.paper import router as paper_router
from app.api.bots import router as bots_router
from app.api.quantum_pro_bots import router as quantum_pro_bots_router
from app.api.trading import router as trading_router
from app.api.portfolio_manager import router as portfolio_manager_router
from app.api.quantum_ai_v2 import router as quantum_ai_v2_router

from app.ai.bot_auto_runner import start_bot_runner

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(market_router)
app.include_router(news_router)
app.include_router(portfolio_router)
app.include_router(watchlist_router)
app.include_router(ai_router)
app.include_router(playbook_router)
app.include_router(scanner_router)
app.include_router(intelligence_router)
app.include_router(opportunities_router)
app.include_router(orderbook_router)
app.include_router(paper_router)
app.include_router(bots_router)
app.include_router(quantum_pro_bots_router)
app.include_router(trading_router)
app.include_router(portfolio_manager_router)
app.include_router(quantum_ai_v2_router)

@app.on_event("startup")
async def startup_event():
    start_bot_runner()


@app.get("/")
def home():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "ONLINE",
        "auth": "DEV_MODE",
        "cors": "ACTIVE",
        "market": "ACTIVE",
        "bots": "ACTIVE",
        "quantum_pro_bots": "ACTIVE",
        "testnet": "ACTIVE",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}