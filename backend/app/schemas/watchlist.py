from pydantic import BaseModel


class WatchlistCreate(BaseModel):
    symbol: str
    asset_type: str = "crypto"