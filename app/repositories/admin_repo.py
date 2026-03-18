from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.db.models.item import ItemModel
from app.db.models.user import UserModel


class AdminRepository:
    def get_all_items(self, db: Session, page: int = 1, size: int = 10):
        """Fetch paginated items."""
        skip = (page - 1) * size

        return db.scalars(select(ItemModel).offset(skip).limit(size)).all()

    def get_all_users(self, db: Session, page: int = 1, size: int = 10):
        """Fetch paginated users."""
        skip = (page - 1) * size

        return db.scalars(select(UserModel).offset(skip).limit(size)).all()

    # SELECT it.id, it.title, it.desc, it.active, it.owner_id, us.username, us.email
    # from items it
    # join users us
    # on it.owner_id = us.id
    def get_all_detailed_items(self, db: Session, page: int = 1, size: int = 10):
        skip = (page - 1) * size
        query = (
            select(
                ItemModel.id,
                ItemModel.title,
                ItemModel.desc,
                ItemModel.active,
                ItemModel.owner_id,
                UserModel.username,
                UserModel.email,
            )
            .join(UserModel, ItemModel.owner_id == UserModel.id)
            .offset(skip)
            .limit(size)
        )
        # query = (
        #     select(ItemModel)
        #     .options(
        #         # Eagerly load the 'owner' relationship using a JOIN
        #         joinedload(ItemModel.owner)
        #         # Only fetch specific columns from the joined User table
        #         .load_only(UserModel.username, UserModel.email)
        #     )
        #     .offset(skip)
        #     .limit(size)
        # )
        return db.execute(query).all()

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
