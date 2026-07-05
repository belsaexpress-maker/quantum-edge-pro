from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import not_found
from app.core.security import get_current_user
from app.database.database import get_db
from app.models.portfolio import PortfolioAsset
from app.repositories.user_repository import get_user_by_username
from app.schemas.portfolio import PortfolioAssetCreate

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.get("/")
def list_portfolio(
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = get_user_by_username(db, username)

    if not user:
        not_found("Kullanıcı bulunamadı")

    assets = db.query(PortfolioAsset).filter(
        PortfolioAsset.user_id == user.id
    ).all()

    return assets


@router.post("/")
def add_asset(
    asset: PortfolioAssetCreate,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = get_user_by_username(db, username)

    if not user:
        not_found("Kullanıcı bulunamadı")

    new_asset = PortfolioAsset(
        user_id=user.id,
        symbol=asset.symbol.upper(),
        asset_type=asset.asset_type,
        quantity=asset.quantity,
        buy_price=asset.buy_price,
    )

    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)

    return {
        "message": "Portföye eklendi",
        "asset": new_asset,
    }


@router.get("/summary")
def portfolio_summary(
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = get_user_by_username(db, username)

    if not user:
        not_found("Kullanıcı bulunamadı")

    assets = db.query(PortfolioAsset).filter(
        PortfolioAsset.user_id == user.id
    ).all()

    total_cost = 0

    for asset in assets:
        total_cost += asset.quantity * asset.buy_price

    return {
        "user": username,
        "asset_count": len(assets),
        "total_cost": round(total_cost, 2),
        "currency": "USD",
    }