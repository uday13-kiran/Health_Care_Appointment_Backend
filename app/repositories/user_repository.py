from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def get_by_email(self, db: Session, email: str):
        return db.scalar(select(User).where(User.email == email))

    def get_by_id(self, db: Session, user_id: int):
        return db.get(User, user_id)

    def create(self, db: Session, user: User):
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
