from typing import Annotated
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.db.database import get_db
from app.service.auth_service import AuthService
from app.repositories.users_repo import UserRepository
from app.repositories.item_repo import ItemRepository
from app.repositories.admin_repo import AdminRepository
from app.db.models.user import UserModel

security = HTTPBearer()

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

admin_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate admin credentials",
)


def get_auth_service() -> AuthService:
    return AuthService()


def get_user_repo() -> UserRepository:
    return UserRepository()


def get_item_repo() -> ItemRepository:
    return ItemRepository()


def get_admin_repo() -> AdminRepository:
    return AdminRepository()


db_dep = Annotated[Session, Depends(get_db)]
auth_service = Annotated[AuthService, Depends(get_auth_service)]
user_repo_dep = Annotated[UserRepository, Depends(get_user_repo)]
item_repo_dep = Annotated[ItemRepository, Depends(get_item_repo)]
admin_repo_dep = Annotated[AdminRepository, Depends(get_admin_repo)]


def get_current_user(
    token_data: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: db_dep,
    auth_service: auth_service,
    user_repo: user_repo_dep,
) -> UserModel:

    token = token_data.credentials

    try:
        payload = auth_service.decode_token(token)
        if payload is None:
            raise credentials_exception

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except Exception:
        raise credentials_exception

    user = user_repo.get_by_id(db, int(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if hasattr(user, "is_active") and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    return user


current_user_dep = Annotated[UserModel, Depends(get_current_user)]


def get_admin(
    current_user: current_user_dep,
) -> UserModel:
    if not getattr(current_user, "is_admin", False):
        raise admin_exception
    return current_user


admin_dep = Annotated[UserModel, Depends(get_admin)]
