from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.favorite import Favorite


class FavoriteRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        property_id: int,
    ) -> Favorite:
        favorite = Favorite(
            user_id=user_id,
            property_id=property_id,
        )

        self.db.add(favorite)
        self.db.commit()
        self.db.refresh(favorite)

        return favorite

    def get_by_user_and_property(
        self,
        user_id: int,
        property_id: int,
    ) -> Favorite | None:
        statement = (
            select(Favorite)
            .where(
                Favorite.user_id == user_id,
                Favorite.property_id == property_id,
            )
        )

        return self.db.scalar(statement)

    def delete(self, favorite: Favorite) -> None:
        self.db.delete(favorite)
        self.db.commit()

    def get_user_favorites(
        self,
        user_id: int,
    ) -> list[Favorite]:
        statement = (
            select(Favorite)
            .options(
                selectinload(Favorite.property)
            )
            .where(
                Favorite.user_id == user_id
            )
            .order_by(
                Favorite.created_at.desc()
            )
        )

        return list(
            self.db.scalars(statement).all()
        )