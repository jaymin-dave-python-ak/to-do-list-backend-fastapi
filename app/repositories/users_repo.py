from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import UserModel


class UserRepository:
    async def get_by_email(self, db: AsyncSession, email: str):
        """Finds a user by email for login/validation."""
        return await db.scalar(select(UserModel).where(UserModel.email == email))

    async def get_by_id(self, db: AsyncSession, user_id: int):
        """Finds a user by ID for the 'get_current_user' logic."""
        return await db.get(UserModel, user_id)

    async def create(self, db: AsyncSession, user_data: dict):
        """Saves a new user to the DB."""
        new_user = UserModel(**user_data)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
