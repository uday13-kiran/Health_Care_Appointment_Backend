from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.permissions.roles import ADMIN

router = APIRouter(prefix="/admin", tags=["Admin"])
service = AuthService()


@router.post("/users", response_model=UserResponse)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(ADMIN)),
):
    user = service.create_user(db, data.email, data.password, data.role)
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role.name,
        "is_active": user.is_active,
    }
