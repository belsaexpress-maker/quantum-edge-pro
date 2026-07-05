def get_bot_templates():
    return [
        {
            "id": "spot_grid",
            "name": "Spot Grid Bot",
            "strategy": "GRID",
            "risk": "Medium",
            "description": "Yatay piyasada kontrollu grid seviyeleriyle kucuk kar hedefler.",
            "default_tp_percent": 0.60,
            "default_sl_percent": 0.35,
            "default_daily_trades": 20,
            "min_interval_seconds": 60,
            "grid_levels": 6,
            "grid_range_percent": 1.2,
        },
        {
            "id": "scalping",
            "name": "Scalping Bot",
            "strategy": "SCALPING",
            "risk": "High",
            "description": "Hizli hareketlerde kontrollu mikro kar hedefler.",
            "default_tp_percent": 0.60,
            "default_sl_percent": 0.35,
            "default_daily_trades": 20,
            "min_interval_seconds": 60,
        },
        {
            "id": "dca",
            "name": "DCA Bot",
            "strategy": "DCA",
            "risk": "Medium",
            "description": "Dususte sadece 1 kez kontrollu ek alim yapar.",
            "default_tp_percent": 0.80,
            "default_sl_percent": 0.60,
            "default_daily_trades": 10,
            "min_interval_seconds": 120,
            "dca_step_percent": 0.80,
            "max_dca_orders": 1,
        },
        {
            "id": "momentum",
            "name": "Momentum Bot",
            "strategy": "MOMENTUM",
            "risk": "Medium",
            "description": "Hacimli ve guclu yukselisleri takip eder.",
            "default_tp_percent": 0.70,
            "default_sl_percent": 0.40,
            "default_daily_trades": 15,
            "min_interval_seconds": 90,
        },
        {
            "id": "breakout",
            "name": "Breakout Bot",
            "strategy": "BREAKOUT",
            "risk": "High",
            "description": "Kirilim yapan coinlerde kontrollu giris yapar.",
            "default_tp_percent": 0.85,
            "default_sl_percent": 0.45,
            "default_daily_trades": 12,
            "min_interval_seconds": 120,
        },
        {
            "id": "mean_reversion",
            "name": "Mean Reversion Bot",
            "strategy": "MEAN_REVERSION",
            "risk": "Medium",
            "description": "Asiri dusen fakat hacmi guclu coinlerde tepki arar.",
            "default_tp_percent": 0.65,
            "default_sl_percent": 0.45,
            "default_daily_trades": 12,
            "min_interval_seconds": 120,
        },
        {
            "id": "quantum_ai",
            "name": "Quantum AI Bot",
            "strategy": "AI",
            "risk": "Controlled",
            "description": "AI Scanner ile en guclu ve guvenli firsatlari secer.",
            "default_tp_percent": 0.75,
            "default_sl_percent": 0.40,
            "default_daily_trades": 15,
            "min_interval_seconds": 90,
        },
    ]


def should_open_position(strategy: str, item: dict):
    if not item:
        return False

    symbol = str(item.get("symbol", "")).upper()
    confidence = float(item.get("confidence", 0) or 0)
    direction = str(item.get("direction", "")).upper()
    change_24h = float(item.get("change_24h", 0) or 0)
    volume_24h = float(item.get("volume_24h", 0) or 0)

    if not is_safe_symbol(symbol):
        return False

    if volume_24h < 100_000:
        return False

    if abs(change_24h) > 25:
        return False

    strategy = strategy.upper()

    if strategy == "SCALPING":
        return confidence >= 55 and abs(change_24h) <= 8

    if strategy == "GRID":
        return confidence >= 50 and abs(change_24h) <= 5

    if strategy == "DCA":
        return confidence >= 50 and -8 <= change_24h <= 2

    if strategy == "MOMENTUM":
        return confidence >= 65 and direction == "LONG" and 0.5 <= change_24h <= 12

    if strategy == "BREAKOUT":
        return confidence >= 70 and direction == "LONG" and 1 <= change_24h <= 15

    if strategy == "MEAN_REVERSION":
        return confidence >= 55 and -12 <= change_24h <= -1

    if strategy == "AI":
        return confidence >= 68 and direction in ["LONG", "WAIT"]

    return confidence >= 60


def can_reenter(strategy: str, item: dict, preferred_symbol: str = "AUTO"):
    if preferred_symbol and preferred_symbol.upper() != "AUTO":
        return True

    return should_open_position(strategy, item)


def build_grid_levels(entry_price: float, levels: int = 6, range_percent: float = 1.2):
    entry_price = float(entry_price or 0)

    if entry_price <= 0:
        return []

    levels = max(2, min(int(levels or 6), 10))
    range_percent = max(0.5, min(float(range_percent or 1.2), 3.0))

    step = range_percent / levels
    grid = []

    for i in range(1, levels + 1):
        up_price = entry_price * (1 + (step * i / 100))
        grid.append(round(up_price, 8))

    return grid


def is_safe_symbol(symbol: str):
    clean = symbol.upper().replace("/", "").replace("_", "")

    if not clean.endswith("USDT"):
        return False

    blocked_parts = [
        "3L",
        "3S",
        "5L",
        "5S",
        "BULL",
        "BEAR",
        "UPUSDT",
        "DOWNUSDT",
    ]

    for part in blocked_parts:
        if part in clean:
            return False

    return True