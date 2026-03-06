from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models.item import ItemModel
from app.db.models.user import UserModel


class AdminRepository:
    def get_all_items(self, db: Session):
        """Fetch all items."""
        return db.scalars(select(ItemModel)).all()

    def get_all_users(self, db: Session):
        """Fetch all users."""
        return db.scalars(select(UserModel)).all()
