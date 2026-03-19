import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from app.db.models.item import ItemStatus, DeactivationType

class ItemBaseSchema(BaseModel):
    title: str
    desc: Optional[str] = None
    status: ItemStatus = ItemStatus.pending
    remind_me_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class ItemCreateSchema(ItemBaseSchema):
    pass

class ItemUpdateSchema(BaseModel):
    title: Optional[str] = None
    desc: Optional[str] = None
    status: Optional[ItemStatus] = None
    remind_me_at: Optional[datetime] = None
    deactivation_type: Optional[DeactivationType] = None
    model_config = ConfigDict(from_attributes=True)

class ItemOutSchema(ItemBaseSchema):
    id: uuid.UUID  
    owner_id: uuid.UUID
    reminded: bool
    deactivation_type: DeactivationType
    created_at: datetime
    last_updated_at: datetime

class ItemOutDetailedSchema(ItemOutSchema):
    username: str
    email: EmailStr
