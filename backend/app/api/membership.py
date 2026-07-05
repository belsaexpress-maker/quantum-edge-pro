from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user_payload, require_admin
from app.database.database import get_db
from app.models.user import User


router = APIRouter(prefix="/membership", tags=["Membership"])


class GrantRoleRequest(BaseModel):
    email: str
    role: str


@router.get("/me")
def membership_me(
    payload: dict = Depends(get_current_user_payload),
):
    role = payload.get("role", "free")

    return {
        "email": payload.get("email"),
        "role": role,
        "can_use_bots": role in ["admin", "paid", "gift"],
        "plan_name": get_plan_name(role),
    }


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    users = db.query(User).order_by(User.id.desc()).all()

    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": str(user.created_at),
        }
        for user in users
    ]


@router.post("/grant-role")
def grant_role(
    payload: GrantRoleRequest,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    role = payload.role.lower()

    if role not in ["admin", "paid", "gift", "free"]:
        raise HTTPException(status_code=400, detail="Geçersiz rol")

    user = db.query(User).filter(User.email == payload.email.lower()).first()

    if not user:
        user = User(
            email=payload.email.lower(),
            full_name=None,
            picture=None,
            google_sub=None,
            role=role,
            is_active=True,
        )
        db.add(user)
    else:
        user.role = role
        user.is_active = True

    db.commit()
    db.refresh(user)

    return {
        "message": "Kullanıcı rolü güncellendi",
        "user": {
            "email": user.email,
            "role": user.role,
        },
    }


def get_plan_name(role: str):
    if role == "admin":
        return "Admin sınırsız erişim"

    if role == "paid":
        return "Ücretli Pro üyelik"

    if role == "gift":
        return "Hediye Pro üyelik"

    return "Free üyelik"