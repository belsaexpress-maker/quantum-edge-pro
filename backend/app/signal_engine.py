def generate_signal(change: float):
    try:
        change = float(change)
    except Exception:
        return "NO DATA ⚪"

    if change > 3:
        return "STRONG BUY 🚀"
    elif change > 1:
        return "BUY 🟢"
    elif -1 <= change <= 1:
        return "HOLD ⚪"
    elif change < -3:
        return "STRONG SELL 🔴"
    else:
        return "SELL 🟠"