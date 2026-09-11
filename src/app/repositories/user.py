from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_data: UserCreate,
        hashed_password: str,
    ) -> User:

        user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def get_by_id(self, user_id: int) -> User | None:
        statement = select(User).where(User.id == user_id)

        return self.db.scalar(statement)

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)

        return self.db.scalar(statement)

    def get_all(self) -> list[User]:
        statement = select(User)

        return list(self.db.scalars(statement).all())
    
    def update(
        self,
        user: User,
        name: str,
        email: str,
    ) -> User:
        user.name = name
        user.email = email

        self.db.commit()
        self.db.refresh(user)

        return user
    
    def update_status(
        self,
        user: User,
        is_active: bool,
    ) -> User:
        user.is_active = is_active

        self.db.commit()
        self.db.refresh(user)

        return user