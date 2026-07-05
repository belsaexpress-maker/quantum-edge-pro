def generate_market_signal(change_24h: float) -> str:
    try:
        value = float(change_24h)
    except Exception:
        return "NO DATA ⚪"

    if value >= 5:
        return "STRONG BUY 🚀"
    if value >= 2:
        return "BUY 🟢"
    if -2 < value < 2:
        return "HOLD ⚪"
    if value <= -5:
        return "STRONG SELL 🔴"

    return "SELL 🟠"