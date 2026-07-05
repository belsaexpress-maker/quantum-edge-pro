from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from app.database.base import Base


class PortfolioAsset(Base):
    __tablename__ = "portfolio_assets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    symbol = Column(String, index=True, nullable=False)
    asset_type = Column(String, default="crypto", nullable=False)

    quantity = Column(Float, default=0)
    buy_price = Column(Float, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)