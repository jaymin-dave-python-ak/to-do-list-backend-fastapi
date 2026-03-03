from pydantic import BaseModel
from typing import Optional


class ItemSchema(BaseModel):
    title: str
    desc: Optional[str] = None
    active: bool = True
