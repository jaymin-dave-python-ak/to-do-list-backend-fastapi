from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models.item import ItemModel


class ItemRepository:
    def get_by_id(self, item_id: int, db: Session):
        """Fetch a single item by ID."""
        return db.scalar(select(ItemModel).where(ItemModel.id == item_id))

    def get_all(self, owner_id: int, db: Session):
        """Fetch all items with current user's owner_id."""
        return db.scalars(select(ItemModel).where(ItemModel.owner_id == owner_id)).all()

    def get_by_title(self, title: str, owner_id: int, db: Session):
        """Fetch a single item by Title."""
        return db.scalar(
            select(ItemModel).where(
                ItemModel.title == title, ItemModel.owner_id == owner_id
            )
        )

    def create(self, item, owner_id: int, db: Session):
        """Add a new item to the list."""
        new_item = ItemModel(**item.model_dump(), owner_id=owner_id)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

    def update(self, item_id: int, update_data: dict, db: Session):
        """Update an existing item (Partial update)."""
        item = self.get_by_id(item_id, db)
        if item:
            for key, value in update_data.items():
                setattr(item, key, value)
            db.commit()
            db.refresh(item)
        return item

    def delete(self, item_id: int, db: Session):
        """Remove an item from the list."""
        item = self.get_by_id(item_id, db)
        if item:
            db.delete(item)
            db.commit()
        return item
