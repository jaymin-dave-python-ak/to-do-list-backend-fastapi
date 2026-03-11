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
@log_func
def login(
    user_in: UserInSchema,
    db: db_dep,
    user_repo: user_repo_dep,
    auth_service: auth_service,
):
    """Authenticate user credentials and generate a JWT access token for successful login."""
    user = user_repo.get_by_email(db, user_in.email)
    if not user or not auth_service.verify_password(
        user_in.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token = auth_service.create_access_token(data={"sub": str(user.id)})

    token_data = {"access_token": token, "token_type": "bearer"}
    return create_response(token_data, "Login successful.")
