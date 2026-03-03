from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBaseSchema(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    is_active: bool = True


class UserCreateSchema(UserBaseSchema):
    password: str = Field(..., min_length=8, description="Plain text password")


class UserOutSchema(UserBaseSchema):
    id: int
    created_at: datetime


class UserInDBSchema(UserOutSchema):
    hashed_password: str


class UserInSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Plain text password")
