from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.core.config import settings
import jwt
import random
from typing import Any
import secrets

# Setup the password hashing context
# 'bcrypt' is the algorithm; 'deprecated="auto"' handles future upgrades
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain text password using bcrypt via Passlib."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify whether a plain password matches the stored bcrypt hashed password."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def _generate_token(
        data: dict, expires_delta: timedelta, secret: str, token_type: str
    ) -> str:
        """Internal helper to generate JWT tokens."""
        to_encode = data.copy()

        if "sub" in to_encode and not isinstance(to_encode["sub"], str):
            to_encode["sub"] = str(to_encode["sub"])

        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire, "type": token_type})
        return jwt.encode(to_encode, secret, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_access_token(data: dict) -> str:
        """Generate a short-lived access token."""
        return AuthService._generate_token(
            data=data,
            expires_delta=timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)),
            secret=settings.SECRET_ACCESS_KEY,
            token_type="access",
        )

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Generate a long-lived refresh token."""
        return AuthService._generate_token(
            data=data,
            expires_delta=timedelta(days=int(settings.REFRESH_TOKEN_EXPIRE_DAYS)),
            secret=settings.SECRET_REFRESH_KEY,
            token_type="refresh",
        )

    @staticmethod
    def decode_token(token: str, is_refresh: bool = False) -> dict[str, Any] | None:
        """Decode token using secret key based on its type."""
        if is_refresh:
            secret = settings.SECRET_REFRESH_KEY
        else:
            secret = settings.SECRET_ACCESS_KEY

        try:
            return jwt.decode(token, secret, algorithms=[settings.ALGORITHM])
        except jwt.PyJWTError:
            return None

    @staticmethod
    def generate_otp() -> str:
        """Generate a cryptographically secure 6-digit OTP."""
        return "".join(secrets.choice("0123456789") for _ in range(6))