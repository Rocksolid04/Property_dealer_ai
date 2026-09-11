from sqlalchemy.orm import Session

from app.core.security import hash_password

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserStatusUpdate


class UserService:

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def create_user(self, user_data: UserCreate):

        existing_user = self.repository.get_by_email(user_data.email)

        if existing_user:
            raise ValueError("Email already registered")

        hashed_password = hash_password(user_data.password)

        return self.repository.create(
            user_data=user_data,
            hashed_password=hashed_password,
        )

    def get_user(self, user_id: int):
        return self.repository.get_by_id(user_id)

    def get_users(self):
        return self.repository.get_all()
    
    def update_user(
        self,
        user: User,
        user_data: UserUpdate,
    ) -> User:
        return self.repository.update(
            user,
            user_data.name,
            user_data.email,
        )
        
    def update_user_status(
        self,
        user: User,
        user_data: UserStatusUpdate,
    ) -> User:
        return self.repository.update_status(
            user,
            user_data.is_active,
        )