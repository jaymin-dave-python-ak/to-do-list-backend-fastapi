from fastapi import APIRouter, status, HTTPException, Depends
from typing import Annotated
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.users_repo import UserRepository
from app.api.v1.schemas.response import ResponseSchema
from app.api.v1.schemas.user import UserCreateSchema, UserInSchema, UserOutSchema
from app.service.auth_service import AuthService

router = APIRouter(prefix="/users", tags=["Users"])
repo = UserRepository()
auth = AuthService()
DBDep = Annotated[Session, Depends(get_db)]


@router.post(
    "/register", response_model=UserOutSchema, status_code=status.HTTP_201_CREATED
)
def register(user_in: UserCreateSchema, db: DBDep):
    if repo.get_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = auth.hash_password(user_in.password)
    user_data = user_in.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed

    return repo.create(db, user_data)


@router.post("/login")
def login(user_in: UserInSchema, db: Session = Depends(get_db)):
    user = repo.get_by_email(db, user_in.email)
    if not user or not auth.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token(data={"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}
