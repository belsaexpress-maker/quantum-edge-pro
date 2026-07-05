from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_current_user_payload
from app.database.database import get_db
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


def user_to_dict(user: User):
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "picture": user.picture,
        "role": user.role,
        "is_active": user.is_active,
    }


def build_token(user: User):
    return create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }
    )


@router.post("/demo-admin")
def demo_admin_login(db: Session = Depends(get_db)):
    email = "belsaexpress@gmail.com"

    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(
            email=email,
            full_name="Admin",
            picture=None,
            google_sub="demo-admin",
            role="admin",
            is_active=True,
        )
        db.add(user)
    else:
        user.role = "admin"
        user.is_active = True

    db.commit()
    db.refresh(user)

    return {
        "access_token": build_token(user),
        "token_type": "bearer",
        "user": user_to_dict(user),
    }


@router.get("/me")
def me(payload: dict = Depends(get_current_user_payload)):
    return payload