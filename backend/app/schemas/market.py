from pydantic import BaseModel


class MarketAsset(BaseModel):
    symbol: str
    name: str
    asset_type: str
    price: float
    change_24h: float
    signal: str