from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Annotated, TYPE_CHECKING
from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.item import ItemModel


IntPK = Annotated[int, mapped_column(primary_key=True, index=True)]


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[IntPK]
    username: Mapped[str] = mapped_column(index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    items: Mapped[list["ItemModel"]] = relationship("ItemModel", back_populates="owner")
