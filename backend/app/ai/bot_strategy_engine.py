def get_bot_templates():
    return [
        {
            "id": "spot_grid",
            "name": "Spot Grid Bot",
            "strategy": "GRID",
            "risk": "Medium",
            "description": "Yatay piyasada grid seviyeleriyle küçük kar hedefler.",
            "default_tp_percent": 0.20,
            "default_sl_percent": 0.60,
            "default_daily_trades": 100,
            "min_interval_seconds": 10,
            "grid_levels": 12,
            "grid_range_percent": 2.0,
        },
        {
            "id": "scalping",
            "name": "Scalping Bot",
            "strategy": "SCALPING",
            "risk": "High",
            "description": "Hızlı küçük hareketlerde mikro kar hedefler.",
            "default_tp_percent": 0.15,
            "default_sl_percent": 0.50,
            "default_daily_trades": 150,
            "min_interval_seconds": 10,
        },
        {
            "id": "dca",
            "name": "DCA Bot",
            "strategy": "DCA",
            "risk": "Medium",
            "description": "Düşüşlerde kademeli alım, toparlanmada kar alır.",
            "default_tp_percent": 0.35,
            "default_sl_percent": 2.00,
            "default_daily_trades": 80,
            "min_interval_seconds": 15,
            "dca_step_percent": 0.50,
            "max_dca_orders": 5,
        },
        {
            "id": "momentum",
            "name": "Momentum Bot",
            "strategy": "MOMENTUM",
            "risk": "Medium",
            "description": "Hacimli yükselişleri takip eder.",
            "default_tp_percent": 0.35,
            "default_sl_percent": 0.80,
            "default_daily_trades": 80,
            "min_interval_seconds": 10,
        },
        {
            "id": "breakout",
            "name": "Breakout Bot",
            "strategy": "BREAKOUT",
            "risk": "High",
            "description": "Kırılım yapan coinlerde hızlı giriş/çıkış yapar.",
            "default_tp_percent": 0.40,
            "default_sl_percent": 0.90,
            "default_daily_trades": 70,
            "min_interval_seconds": 10,
        },
        {
            "id": "mean_reversion",
            "name": "Mean Reversion Bot",
            "strategy": "MEAN_REVERSION",
            "risk": "Medium",
            "description": "Aşırı düşen coinlerde tepki alımı arar.",
            "default_tp_percent": 0.25,
            "default_sl_percent": 0.80,
            "default_daily_trades": 100,
            "min_interval_seconds": 10,
        },
        {
            "id": "quantum_ai",
            "name": "Quantum AI Bot",
            "strategy": "AI",
            "risk": "Controlled",
            "description": "AI Scanner ile en güçlü fırsatları seçer.",
            "default_tp_percent": 0.30,
            "default_sl_percent": 0.80,
            "default_daily_trades": 120,
            "min_interval_seconds": 10,
        },
    ]


def should_open_position(strategy, scanner_item):
    confidence = scanner_item.get("confidence", 0)
    change = scanner_item.get("change_24h", 0)
    volume = scanner_item.get("volume_24h", 0)
    direction = scanner_item.get("direction", "WAIT")

    if strategy == "GRID":
        return volume > 250000 and -5 <= change <= 5

    if strategy == "SCALPING":
        return confidence >= 55 and volume > 300000

    if strategy == "DCA":
        return volume > 250000 and change <= 1

    if strategy == "MOMENTUM":
        return confidence >= 60 and change > 0.8 and volume > 500000

    if strategy == "BREAKOUT":
        return confidence >= 65 and change > 1.5 and volume > 750000

    if strategy == "MEAN_REVERSION":
        return confidence >= 45 and change < 0 and volume > 250000

    if strategy == "AI":
        return confidence >= 60 and direction in ["LONG", "WAIT"]

    return False


def build_grid_levels(entry_price, grid_levels=12, grid_range_percent=2.0):
    lower = entry_price * (1 - grid_range_percent / 100)
    upper = entry_price * (1 + grid_range_percent / 100)

    if grid_levels <= 1:
        return [round(entry_price, 8)]

    step = (upper - lower) / (grid_levels - 1)

    return [round(lower + step * i, 8) for i in range(grid_levels)]


def can_reenter(strategy, scanner_item, last_symbol=None):
    if scanner_item.get("symbol") == last_symbol:
        return scanner_item.get("confidence", 0) >= 75

    return should_open_position(strategy, scanner_item)