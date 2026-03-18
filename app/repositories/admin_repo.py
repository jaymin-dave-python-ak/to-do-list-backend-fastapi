from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.item import ItemModel
from app.db.models.user import UserModel


class AdminRepository:
    async def get_all_items(self, db: AsyncSession, page: int = 1, size: int = 10):
        """Fetch paginated items."""
        skip = (page - 1) * size
        result = await db.scalars(select(ItemModel).offset(skip).limit(size))
        return result.all()

    async def get_all_users(self, db: AsyncSession, page: int = 1, size: int = 10):
        """Fetch paginated users."""
        skip = (page - 1) * size
        result = await db.scalars(select(UserModel).offset(skip).limit(size))
        return result.all()

    # SELECT it.id, it.title, it.desc, it.active, it.owner_id, us.username, us.email
    # from items it
    # join users us
    # on it.owner_id = us.id
    async def get_all_detailed_items(
        self, db: AsyncSession, page: int = 1, size: int = 10
    ):
        """Fetch paginated items with user data."""
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
        # Use await with db.execute()
        result = await db.execute(query)
        return result.all()
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
        # return db.execute(query).all()

    async def get_item_by_id(self, item_id: int, db: AsyncSession):
        """Fetch single item by Item ID."""
        return await db.get(ItemModel, item_id)

    async def get_user_by_id(self, user_id: int, db: AsyncSession):
        """Fetch single user by its User ID."""
        return await db.get(UserModel, user_id)

    async def get_item_by_title(self, title: str, owner_id: int, db: AsyncSession):
        """Fetch a single item by Title."""
        result = await db.scalar(
            select(ItemModel).where(
                ItemModel.title == title, ItemModel.owner_id == owner_id
            )
        )
        return result

    async def create_item(self, item, owner_id: int, db: AsyncSession):
        """Add a new item to the list."""
        new_item = ItemModel(**item.model_dump(), owner_id=owner_id)
        db.add(new_item)
        await db.commit()
        await db.refresh(new_item)
        return new_item

    async def update_item(self, item_id: int, update_data: dict, db: AsyncSession):
        """Update an existing item (Partial update)."""
        item = await self.get_item_by_id(item_id, db)
        if item:
            for key, value in update_data.items():
                setattr(item, key, value)
            await db.commit()
            await db.refresh(item)
        return item

    async def update_user(self, user_id: int, update_data: dict, db: AsyncSession):
        """Update an existing user (Partial update)."""
        user = await self.get_user_by_id(user_id, db)
        if user:
            for key, value in update_data.items():
                setattr(user, key, value)
            await db.commit()
            await db.refresh(user)
        return user

    async def delete_item(self, item_id: int, db: AsyncSession):
        """Remove an item from the list."""
        item = await self.get_item_by_id(item_id, db)
        if item:
            await db.delete(item)
            await db.commit()
        return item
