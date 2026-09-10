from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.favorite import FavoriteService

from app.core.security import get_current_user


router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"],
)


@router.post("/{property_id}")
def add_favorite(
    property_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = FavoriteService(db)

    return service.add_favorite(
        user_id=current_user.id,
        property_id=property_id,
    )


@router.delete("/{property_id}")
def remove_favorite(
    property_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = FavoriteService(db)

    return service.remove_favorite(
        user_id=current_user.id,
        property_id=property_id,
    )


@router.get("")
def get_favorites(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    service = FavoriteService(db)

    return service.get_user_favorites(
        user_id=current_user.id,
    )