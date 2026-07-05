from datetime import datetime, timedelta


class MarketCache:
    def __init__(self):
        self.data = {
            "crypto": [],
            "stocks": [],
            "indices": [],
            "commodities": [],
            "forex": [],
        }
        self.last_updated = None

    def is_fresh(self, seconds: int = 5) -> bool:
        if self.last_updated is None:
            return False

        return datetime.utcnow() - self.last_updated < timedelta(seconds=seconds)

    def set_crypto(self, items):
        self.data["crypto"] = items
        self.last_updated = datetime.utcnow()

    def get_all(self):
        return {
            **self.data,
            "meta": {
                "last_updated": self.last_updated.isoformat()
                if self.last_updated
                else None,
                "crypto_count": len(self.data["crypto"]),
                "source": "Market Data Engine",
            },
        }


market_cache = MarketCache()