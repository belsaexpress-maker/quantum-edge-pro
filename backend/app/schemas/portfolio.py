from pydantic import BaseModel


class PortfolioAssetCreate(BaseModel):
    symbol: str
    asset_type: str = "crypto"
    quantity: float
    buy_price: float


class PortfolioAssetResponse(BaseModel):
    id: int
    symbol: str
    asset_type: str
    quantity: float
    buy_price: float

    class Config:
        from_attributes = True


class PortfolioSummary(BaseModel):
    total_cost: float
    total_value: float
    profit_loss: float
    profit_loss_percent: float