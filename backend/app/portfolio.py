def calculate_portfolio_summary(items: list):
    total_cost = 0
    total_value = 0

    for item in items:
        quantity = float(item.get("quantity", 0))
        buy_price = float(item.get("buy_price", 0))
        current_price = float(item.get("current_price", 0))

        total_cost += quantity * buy_price
        total_value += quantity * current_price

    profit_loss = total_value - total_cost

    if total_cost > 0:
        profit_loss_percent = (profit_loss / total_cost) * 100
    else:
        profit_loss_percent = 0

    return {
        "total_cost": round(total_cost, 2),
        "total_value": round(total_value, 2),
        "profit_loss": round(profit_loss, 2),
        "profit_loss_percent": round(profit_loss_percent, 2)
    }