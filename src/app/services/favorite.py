from sqlalchemy.orm import Session

from app.repositories.favorite import FavoriteRepository


class FavoriteService:

    def __init__(self, db: Session):
        self.repository = FavoriteRepository(db)

    def add_favorite(
        self,
        user_id: int,
        property_id: int,
    ):
        existing_favorite = self.repository.get_by_user_and_property(
            user_id=user_id,
            property_id=property_id,
        )

        if existing_favorite:
            return existing_favorite

        return self.repository.create(
            user_id=user_id,
            property_id=property_id,
        )

    def remove_favorite(
        self,
        user_id: int,
        property_id: int,
    ):
        favorite = self.repository.get_by_user_and_property(
            user_id=user_id,
            property_id=property_id,
        )

        if favorite is None:
            return None

        self.repository.delete(favorite)

        return favorite

    def get_user_favorites(
        self,
        user_id: int,
    ):
        return self.repository.get_user_favorites(
            user_id=user_id
        )