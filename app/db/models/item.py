import uuid
from datetime import datetime
import enum
from sqlalchemy import String, ForeignKey, Enum, DateTime, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import TYPE_CHECKING, Optional
from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.user import UserModel


class ItemStatus(enum.Enum):
    running = "running"
    pending = "pending"
    completed = "completed"
    deactivated = "deactivated"


class DeactivationType(enum.Enum):
    manual = "manual"
    automatic = "automatic"
    none = "none"


class ItemModel(Base):
    __tablename__ = "items"

    title: Mapped[str] = mapped_column(String, index=True)
    desc: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    status: Mapped[ItemStatus] = mapped_column(
        Enum(ItemStatus), default=ItemStatus.pending
    )
    deactivation_type: Mapped[DeactivationType] = mapped_column(
        Enum(DeactivationType), default=DeactivationType.none
    )

    remind_me_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True),nullable=True)
    reminded: Mapped[bool] = mapped_column(Boolean, default=False)
    dispatched: Mapped[bool] = mapped_column(Boolean, default=False)

    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    
    owner: Mapped["UserModel"] = relationship("UserModel", back_populates="items")