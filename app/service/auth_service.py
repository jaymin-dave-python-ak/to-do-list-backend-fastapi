from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.core.config import settings
import jwt
from typing import Any

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
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        """Generate a signed JWT access token with expiration time for authenticated sessions."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict[str, Any] | None:
        """Decode and validate a JWT token and return the payload if the signature is valid."""
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.PyJWTError:
            return None
