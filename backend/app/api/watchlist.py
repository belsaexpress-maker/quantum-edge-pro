from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import not_found
from app.core.security import get_current_user
from app.database.database import get_db
from app.models.watchlist import WatchlistItem
from app.repositories.user_repository import get_user_by_username
from app.schemas.watchlist import WatchlistCreate

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


@router.get("/")
def list_watchlist(
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = get_user_by_username(db, username)

    if not user:
        not_found("Kullanıcı bulunamadı")

    items = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == user.id
    ).all()

    return items


@router.post("/")
def add_watchlist_item(
    item: WatchlistCreate,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = get_user_by_username(db, username)

    if not user:
        not_found("Kullanıcı bulunamadı")

    new_item = WatchlistItem(
        user_id=user.id,
        symbol=item.symbol.upper(),
        asset_type=item.asset_type,
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return {
        "message": "Watchlist'e eklendi",
        "item": new_item,
    }