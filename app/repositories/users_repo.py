from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models.user import UserModel


class UserRepository:
    def get_by_email(self, db: Session, email: str):
        """Finds a user by email for login/validation."""
        return db.scalar(select(UserModel).where(UserModel.email == email))

    def get_by_id(self, db: Session, user_id: int):
        """Finds a user by ID for the 'get_current_user' logic."""
        return db.get(UserModel, user_id)

    def create(self, db: Session, user_data: dict):
        """Saves a new user to the DB."""
        new_user = UserModel(**user_data)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
