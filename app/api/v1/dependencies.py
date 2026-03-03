from typing import Annotated
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.db.database import get_db
from app.service.auth_service import AuthService
from app.repositories.users_repo import UserRepository
from app.db.models.user import UserModel

security = HTTPBearer()

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_auth_service() -> AuthService:
    return AuthService()


def get_user_repo() -> UserRepository:
    return UserRepository()


async def get_current_user(
    token_data: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
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
