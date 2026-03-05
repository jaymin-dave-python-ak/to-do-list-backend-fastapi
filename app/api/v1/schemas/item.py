from pydantic import BaseModel, ConfigDict
from typing import Optional


class ItemSchema(BaseModel):
    title: str
    desc: Optional[str] = None
    active: bool = True
    model_config = ConfigDict(from_attributes=True)


class ItemOutSchema(ItemSchema):
    id: int
    owner_id: int
    model_config = ConfigDict(from_attributes=True)
