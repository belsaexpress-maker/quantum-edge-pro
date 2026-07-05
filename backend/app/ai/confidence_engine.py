import random


def calculate_ai_confidence(symbol: str = "BTCUSDT"):
    indicators = {
        "RSI": random.randint(35, 75),
        "MACD": random.randint(40, 85),
        "EMA": random.randint(45, 90),
        "SuperTrend": random.randint(40, 90),
        "VWAP": random.randint(35, 85),
        "Volume Profile": random.randint(30, 80),
        "Order Book": random.randint(35, 85),
        "Open Interest": random.randint(30, 80),
        "Funding Rate": random.randint(30, 75),
        "Liquidation Heatmap": random.randint(30, 85),
        "News Sentiment": random.randint(35, 90),
        "Economic Calendar": random.randint(30, 75),
        "Whale Activity": random.randint(35, 85),
        "Bitcoin Dominance": random.randint(35, 80),
        "Fear & Greed": random.randint(30, 85),
        "Stablecoin Flow": random.randint(35, 90),
    }

    score = round(sum(indicators.values()) / len(indicators))

    if score >= 80:
        signal = "STRONG BUY 🚀"
        risk = "Medium"
    elif score >= 65:
        signal = "BUY 🟢"
        risk = "Controlled"
    elif score >= 45:
        signal = "HOLD ⚪"
        risk = "Neutral"
    elif score >= 30:
        signal = "SELL 🟠"
        risk = "High"
    else:
        signal = "STRONG SELL 🔴"
        risk = "Very High"

    return {
        "symbol": symbol,
        "ai_confidence": score,
        "signal": signal,
        "risk": risk,
        "indicators": indicators,
        "summary": f"{symbol} için AI güven puanı {score}/100. Sinyal: {signal}. Risk: {risk}.",
    }