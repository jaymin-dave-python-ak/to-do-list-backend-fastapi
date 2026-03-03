from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean
from typing import Annotated, Optional
from app.db.models.base import Base

IntPK = Annotated[
    int,
    mapped_column(primary_key=True, index=True),
]
OptionalStr = Annotated[Optional[str], mapped_column(nullable=True)]


class ItemModel(Base):
    __tablename__ = "items"
    id: Mapped[IntPK]
    title: Mapped[str] = mapped_column(String, index=True)
    desc: Mapped[OptionalStr]
    active: Mapped[bool] = mapped_column(Boolean)
