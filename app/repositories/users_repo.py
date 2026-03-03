from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models.user import UserModel


class UserRepository:
    def get_all(self, db: Session):
        """Fetch all Users."""
        return db.scalars(select(UserModel)).all()

    def sign_up(self, user, db: Session):
        """Create and Add a User."""
        new_user = UserModel(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
