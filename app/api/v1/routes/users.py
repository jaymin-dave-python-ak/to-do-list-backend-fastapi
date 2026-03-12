from datetime import datetime, timezone
from fastapi import APIRouter, status, HTTPException
from app.api.v1.dependencies import (
    db_dep,
    redis_dep,
    user_repo_dep,
    auth_service,
    email_service,
)
from app.api.v1.schemas.user import UserCreateSchema, UserInSchema, UserOutSchema
from app.api.v1.schemas.response import ResponseSchema, create_response
from app.core.logger import log_func
import json
from fastapi import BackgroundTasks

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=ResponseSchema)
@log_func
async def register_initiate(
    user_in: UserCreateSchema,
    db: db_dep,
    redis: redis_dep,
    user_repo: user_repo_dep,
    auth_service: auth_service,
    email_service: email_service,
    background_tasks: BackgroundTasks
):
    if user_repo.get_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = auth_service.hash_password(user_in.password)
    otp = auth_service.generate_otp()

    pending_user = user_in.model_dump(exclude={"password"})
    pending_user["hashed_password"] = hashed
    pending_user["otp"] = otp

    # Stored in Redis (TTL: 10 minutes)
    # Key: "pending_user:email@example.com"
    redis.set(f"pending_user:{user_in.email}", json.dumps(pending_user), ex=600)

    background_tasks.add_task(email_service.send_otp_email, user_in.email, otp)

    return create_response(None, "OTP sent to your email. Valid for 10 minutes.")


@router.post("/verify-otp", response_model=ResponseSchema)
@log_func
def verify_otp(
    email: str,
    otp: str,
    db: db_dep,
    redis: redis_dep,
    user_repo: user_repo_dep,
):
    raw_data = redis.get(f"pending_user:{email}")
    if not raw_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired or email not found",
        )

    pending_user = json.loads(raw_data)

    if pending_user["otp"] != otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP"
        )

    # Remove OTP from data before saving
    pending_user.pop("otp")
    new_user = user_repo.create(db, pending_user)

    redis.delete(f"pending_user:{email}")
    
    user_out = UserOutSchema.model_validate(new_user).model_dump()
    return create_response(user_out, "Email verified and user registered successfully.")


@router.post("/login", response_model=ResponseSchema)
@log_func
def login(
    user_in: UserInSchema,
    db: db_dep,
    user_repo: user_repo_dep,
    auth_service: auth_service,
):
    """Authenticate user credentials and generate a JWT access and refresh token for successful login."""
    user = user_repo.get_by_email(db, user_in.email)

    if not user or not auth_service.verify_password(
        user_in.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # Generate both tokens
    access_token = auth_service.create_access_token(data={"sub": str(user.id)})
    refresh_token = auth_service.create_refresh_token(data={"sub": str(user.id)})

    token_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
    return create_response(token_data, "Login successful.")


@router.post("/refresh", response_model=ResponseSchema)
@log_func
def refresh_token(refresh_token: str, auth_service: auth_service, redis: redis_dep):
    """Swap an old refresh token for a brand-new access AND refresh token."""

    payload = auth_service.decode_token(refresh_token, is_refresh=True)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    if redis.exists(f"blacklist:{refresh_token}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has already been used",
        )

    user_id = payload.get("sub")

    new_access_token = auth_service.create_access_token(data={"sub": user_id})
    new_refresh_token = auth_service.create_refresh_token(data={"sub": user_id})

    exp_timestamp = payload.get("exp")
    now = datetime.now(timezone.utc).timestamp()
    ttl = int(exp_timestamp - now)

    if ttl > 0:
        redis.set(f"blacklist:{refresh_token}", "used", ex=ttl)

    token_data = {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }

    return create_response(token_data, "Tokens rotated successfully.")
