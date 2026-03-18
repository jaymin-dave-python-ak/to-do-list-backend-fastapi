from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional


class ItemSchema(BaseModel):
    title: str
    desc: Optional[str] = None
    active: bool = True
    model_config = ConfigDict(from_attributes=True)


class ItemUpdateSchema(BaseModel):
    title: Optional[str] = None
    desc: Optional[str] = None
    active: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)


class ItemOutSchema(ItemSchema):
    id: int
    owner_id: int


class ItemOutDetailedSchema(ItemOutSchema):
    username: str
    email: EmailStr
