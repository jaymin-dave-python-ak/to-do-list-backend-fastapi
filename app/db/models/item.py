from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey
from typing import Annotated, Optional, TYPE_CHECKING
from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.user import UserModel

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
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    owner: Mapped["UserModel"] = relationship("UserModel", back_populates="items")
