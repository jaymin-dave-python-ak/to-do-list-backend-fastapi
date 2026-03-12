from typing import Annotated
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis

from app.db.database import get_db
from app.core.redis import get_redis
from app.service.auth_service import AuthService
from app.service.email_service import EmailService
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
    """Provide AuthService instance used for password hashing and JWT token operations."""
    return AuthService()


def get_email_service() -> EmailService:
    """Provide EmailService instance used for sending an email for OTP verification."""
    return EmailService()


def get_user_repo() -> UserRepository:
    """Provide UserRepository instance to perform database operations related to users."""
    return UserRepository()


def get_item_repo() -> ItemRepository:
    """Provide ItemRepository instance to handle item CRUD operations."""
    return ItemRepository()


def get_admin_repo() -> AdminRepository:
    """Provide AdminRepository instance to manage admin related database operations."""
    return AdminRepository()


db_dep = Annotated[Session, Depends(get_db)]
redis_dep = Annotated[redis.Redis, Depends(get_redis)]
auth_service = Annotated[AuthService, Depends(get_auth_service)]
email_service = Annotated[EmailService, Depends(get_email_service)]
user_repo_dep = Annotated[UserRepository, Depends(get_user_repo)]
item_repo_dep = Annotated[ItemRepository, Depends(get_item_repo)]
admin_repo_dep = Annotated[AdminRepository, Depends(get_admin_repo)]


def get_current_user(
    token_data: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: db_dep,
    auth_service: auth_service,
    user_repo: user_repo_dep,
) -> UserModel:
    """Extract user from JWT token, validate credentials, and return the authenticated user model."""

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
    """Verify that the authenticated user has admin privileges before allowing access."""
    if not getattr(current_user, "is_admin", False):
        raise admin_exception
    return current_user


admin_dep = Annotated[UserModel, Depends(get_admin)]
