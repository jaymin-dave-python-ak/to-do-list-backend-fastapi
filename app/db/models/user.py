from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean
from typing import Annotated
from app.db.models.base import Base

IntPK = Annotated[int, mapped_column(primary_key=True, index=True)]


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[IntPK]
    username: Mapped[str] = mapped_column(String, index=True)
    password: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    active: Mapped[bool] = mapped_column(Boolean)
