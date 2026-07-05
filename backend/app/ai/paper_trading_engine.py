from datetime import datetime

paper_state = {
    "balance": 100000.0,
    "positions": [],
    "orders": [],
}


def get_paper_account():
    total_position_value = sum(
        position["quantity"] * position["current_price"]
        for position in paper_state["positions"]
    )

    total_cost = sum(
        position["quantity"] * position["entry_price"]
        for position in paper_state["positions"]
    )

    unrealized_pnl = total_position_value - total_cost

    return {
        "balance": round(paper_state["balance"], 2),
        "position_count": len(paper_state["positions"]),
        "total_position_value": round(total_position_value, 2),
        "unrealized_pnl": round(unrealized_pnl, 2),
        "equity": round(paper_state["balance"] + total_position_value, 2),
        "positions": paper_state["positions"],
        "orders": paper_state["orders"][-50:],
    }


def create_paper_order(symbol: str, side: str, price: float, quantity: float):
    symbol = symbol.upper()
    side = side.upper()

    order_value = price * quantity

    order = {
        "id": len(paper_state["orders"]) + 1,
        "symbol": symbol,
        "side": side,
        "price": round(price, 8),
        "quantity": quantity,
        "value": round(order_value, 2),
        "created_at": datetime.utcnow().isoformat(),
        "status": "FILLED",
    }

    if side == "BUY":
        if paper_state["balance"] < order_value:
            return {
                "error": "Yetersiz sanal bakiye",
            }

        paper_state["balance"] -= order_value

        existing = next(
            (p for p in paper_state["positions"] if p["symbol"] == symbol),
            None,
        )

        if existing:
            old_value = existing["entry_price"] * existing["quantity"]
            new_value = order_value
            new_quantity = existing["quantity"] + quantity

            existing["entry_price"] = round((old_value + new_value) / new_quantity, 8)
            existing["quantity"] = new_quantity
            existing["current_price"] = price
            existing["unrealized_pnl"] = round(
                (existing["current_price"] - existing["entry_price"])
                * existing["quantity"],
                2,
            )
        else:
            paper_state["positions"].append(
                {
                    "symbol": symbol,
                    "quantity": quantity,
                    "entry_price": round(price, 8),
                    "current_price": round(price, 8),
                    "unrealized_pnl": 0,
                }
            )

    elif side == "SELL":
        existing = next(
            (p for p in paper_state["positions"] if p["symbol"] == symbol),
            None,
        )

        if not existing or existing["quantity"] < quantity:
            return {
                "error": "Satılacak yeterli sanal pozisyon yok",
            }

        paper_state["balance"] += order_value
        existing["quantity"] -= quantity

        if existing["quantity"] <= 0:
            paper_state["positions"] = [
                p for p in paper_state["positions"] if p["symbol"] != symbol
            ]
        else:
            existing["current_price"] = price
            existing["unrealized_pnl"] = round(
                (existing["current_price"] - existing["entry_price"])
                * existing["quantity"],
                2,
            )

    else:
        return {
            "error": "Side sadece BUY veya SELL olabilir",
        }

    paper_state["orders"].append(order)

    return {
        "message": "Paper order filled",
        "order": order,
        "account": get_paper_account(),
    }


def reset_paper_account():
    paper_state["balance"] = 100000.0
    paper_state["positions"] = []
    paper_state["orders"] = []

    return get_paper_account()