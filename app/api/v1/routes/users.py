from fastapi import APIRouter, status, HTTPException
from app.api.v1.dependencies import db_dep, user_repo_dep, auth_service
from app.api.v1.schemas.user import UserCreateSchema, UserInSchema, UserOutSchema
from app.api.v1.schemas.response import ResponseSchema, create_response
from app.core.logger import log_func

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED
)
@log_func
def register(
    user_in: UserCreateSchema,
    db: db_dep,
    user_repo: user_repo_dep,
    auth_service: auth_service,
):
    """Register a new user by validating email uniqueness, hashing password, and storing user in database."""
    if user_repo.get_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    hashed = auth_service.hash_password(user_in.password)
    user_data = user_in.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed

    new_user = user_repo.create(db, user_data)

    user_out = UserOutSchema.model_validate(new_user).model_dump()
    return create_response(user_out, "User registered successfully.")

@router.post("/login", response_model=ResponseSchema)
def login(user_in: UserInSchema, db: db_dep, user_repo: user_repo_dep, auth_service: auth_service):
    """Authenticate user credentials and generate a JWT access and refresh token for successful login."""
    user = user_repo.get_by_email(db, user_in.email)

    if not user or not auth_service.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Generate both tokens
    access_token = auth_service.create_access_token(data={"sub": str(user.id)})
    refresh_token = auth_service.create_refresh_token(data={"sub": str(user.id)})

    token_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
    return create_response(token_data, "Login successful.")

@router.post("/refresh", response_model=ResponseSchema)
def refresh_token(refresh_token: str, auth_service: auth_service):
    """Swap an old refresh token for a brand-new access AND refresh token."""
    
    payload = auth_service.decode_token(refresh_token, is_refresh=True)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired refresh token"
        )
    
    user_id = payload.get("sub")

    new_access_token = auth_service.create_access_token(data={"sub": user_id})
    new_refresh_token = auth_service.create_refresh_token(data={"sub": user_id})
    
    token_data = {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

    # When you implement rotation, 
    # it is best practice to blacklist the old refresh_token in a database (like Redis) so it can't be used again.
    # Without blacklisting, the old token technically remains valid until its original expiry date.
    return create_response(token_data, "Tokens rotated successfully.")