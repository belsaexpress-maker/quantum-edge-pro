def ema(values, period):
    if not values or len(values) < period:
        return None

    multiplier = 2 / (period + 1)
    ema_value = sum(values[:period]) / period

    for price in values[period:]:
        ema_value = (price - ema_value) * multiplier + ema_value

    return round(ema_value, 6)


def rsi(values, period=14):
    if not values or len(values) <= period:
        return None

    gains = []
    losses = []

    for i in range(1, period + 1):
        diff = values[i] - values[i - 1]
        gains.append(max(diff, 0))
        losses.append(abs(min(diff, 0)))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    for i in range(period + 1, len(values)):
        diff = values[i] - values[i - 1]
        gain = max(diff, 0)
        loss = abs(min(diff, 0))

        avg_gain = ((avg_gain * (period - 1)) + gain) / period
        avg_loss = ((avg_loss * (period - 1)) + loss) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    value = 100 - (100 / (1 + rs))

    return round(value, 2)


def macd(values):
    if not values or len(values) < 35:
        return {
            "macd": None,
            "signal": None,
            "histogram": None,
        }

    ema_12 = ema(values, 12)
    ema_26 = ema(values, 26)

    if ema_12 is None or ema_26 is None:
        return {
            "macd": None,
            "signal": None,
            "histogram": None,
        }

    macd_line = ema_12 - ema_26

    macd_values = []
    for i in range(26, len(values)):
        slice_values = values[: i + 1]
        e12 = ema(slice_values, 12)
        e26 = ema(slice_values, 26)

        if e12 is not None and e26 is not None:
            macd_values.append(e12 - e26)

    signal_line = ema(macd_values, 9)

    if signal_line is None:
        return {
            "macd": round(macd_line, 6),
            "signal": None,
            "histogram": None,
        }

    histogram = macd_line - signal_line

    return {
        "macd": round(macd_line, 6),
        "signal": round(signal_line, 6),
        "histogram": round(histogram, 6),
    }


def atr(candles, period=14):
    if not candles or len(candles) <= period:
        return None

    true_ranges = []

    for i in range(1, len(candles)):
        high = candles[i]["high"]
        low = candles[i]["low"]
        previous_close = candles[i - 1]["close"]

        tr = max(
            high - low,
            abs(high - previous_close),
            abs(low - previous_close),
        )

        true_ranges.append(tr)

    value = sum(true_ranges[-period:]) / period

    return round(value, 6)


def calculate_indicators(candles):
    closes = [candle["close"] for candle in candles]

    return {
        "rsi": rsi(closes),
        "ema20": ema(closes, 20),
        "ema50": ema(closes, 50),
        "ema100": ema(closes, 100),
        "ema200": ema(closes, 200),
        "macd": macd(closes),
        "atr": atr(candles),
    }