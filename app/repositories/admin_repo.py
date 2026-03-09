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

    def get_item_by_id(self, item_id: int, db: Session):
        return db.get(ItemModel, item_id)

    def get_user_by_id(self, user_id: int, db: Session):
        return db.get(UserModel, user_id)

    def get_item_by_title(self, title: str, owner_id: int, db: Session):
        """Fetch a single item by Title."""
        return db.scalar(
            select(ItemModel).where(
                ItemModel.title == title, ItemModel.owner_id == owner_id
            )
        )

    def create_item(self, item, owner_id: int, db: Session):
        """Add a new item to the list."""
        new_item = ItemModel(**item.model_dump(), owner_id=owner_id)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

    def update_item(self, item_id: int, update_data: dict, db: Session):
        """Update an existing item (Partial update)."""
        item = self.get_item_by_id(item_id, db)
        if item:
            for key, value in update_data.items():
                setattr(item, key, value)
            db.commit()
            db.refresh(item)
        return item

    def update_user(self, user_id: int, update_data: dict, db: Session):
        """Update an existing user (Partial update)."""
        user = self.get_user_by_id(user_id, db)
        if user:
            for key, value in update_data.items():
                setattr(user, key, value)
            db.commit()
            db.refresh(user)
        return user

    def delete_item(self, item_id: int, db: Session):
        """Remove an item from the list."""
        item = self.get_item_by_id(item_id, db)
        if item:
            db.delete(item)
            db.commit()
        return item
