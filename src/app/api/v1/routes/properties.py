
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.security import require_role, get_current_user
from app.database.dependencies import get_db
from app.models.user import User
from app.repositories.property_image import create_property_image 
from app.schemas.property import (
    PropertyAISearchResponse,
    PropertyCreate,
    PropertyImageResponse,
    PropertyResponse,
    PropertySearchResponse,
    PropertySemanticSearchResponse,
    PropertyOwnerUpdate,
    PropertyStatsResponse,
)
from app.services.property import PropertyService
from app.services.storage import upload_property_image

from app.schemas.search import RAGSearchRequest
from app.services.rag_service import RAGService

from app.services.property_image import (
    delete_image,
    get_images_for_property,
)



router = APIRouter(
    prefix="/properties",
    tags=["Properties"],
)


@router.post(
    "/",
    response_model=PropertyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("dealer", "admin")
    ),
):
    service = PropertyService(db)

    return service.create_property(property_data,current_user.id)

@router.get(
    "/search",
    response_model=PropertySearchResponse,
)
def search_properties(
    location: str | None = None,
    property_type: str | None = None,
    listing_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    bedrooms: int | None = None,
    page: int = 1,
    limit: int = 10,
    sort_by: str = "created_at",
    order: str = "desc",
    db: Session = Depends(get_db),
):
    service = PropertyService(db)

    return service.search_properties(
        location=location,
        property_type=property_type,
        listing_type=listing_type,
        min_price=min_price,
        max_price=max_price,
        bedrooms=bedrooms,
        page=page,
        limit=limit,
        sort_by=sort_by,
        order=order,
    )

@router.get(
    "/semantic-search",
    response_model=list[PropertySemanticSearchResponse],
)
def semantic_search_properties(
    query: str,
    limit: int = 5,
    db: Session = Depends(get_db),
):
    service = PropertyService(db)

    return service.semantic_search(
        query=query,
        limit=limit,
    )

@router.get(
    "/hybrid-search",
    response_model=list[PropertySemanticSearchResponse],
)
def hybrid_search_properties(
    query: str,
    location: str | None = None,
    property_type: str | None = None,
    listing_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    bedrooms: int | None = None,
    limit: int = 5,
    db: Session = Depends(get_db),
):
    service = PropertyService(db)

    return service.hybrid_search(
        query=query,
        location=location,
        property_type=property_type,
        listing_type=listing_type,
        min_price=min_price,
        max_price=max_price,
        bedrooms=bedrooms,
        limit=limit,
    )

@router.get(
    "/ai-search",
    response_model=PropertyAISearchResponse,
)
def ai_search_properties(
    query: str,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty",
        )

    if len(query) > 500:
        raise HTTPException(
            status_code=400,
            detail="Search query is too long. Maximum 500 characters.",
        )

    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than or equal to 1.",
        )

    if limit < 1 or limit > 50:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 50.",
        )

    service = PropertyService(db)

    try:
        return service.ai_search(
            query=query,
            page=page,
            limit=limit,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

@router.get(
    "/",
    response_model=list[PropertyResponse],
)
def get_properties(
    db: Session = Depends(get_db),
):
    service = PropertyService(db)

    return service.get_properties()


@router.post(
    "/{property_id}/images",
    response_model=PropertyImageResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_property_image_endpoint(
    property_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("dealer", "admin")
    ),
):
    service = PropertyService(db)

    property_obj = service.get_property(property_id)

    if property_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    file_content = file.file.read()

    unique_filename = f"{uuid4()}_{file.filename}"

    storage_path = f"{property_id}/{unique_filename}"

    result = upload_property_image(
        file_content=file_content,
        file_path=storage_path,
        content_type=file.content_type or "application/octet-stream",
    )

    image = create_property_image(
        db=db,
        property_id=property_id,
        image_url=result["public_url"],
        storage_path=result["storage_path"],
    )

    return image

@router.get(
    "/{property_id}/images",
    response_model=list[PropertyImageResponse],
)
def get_property_images_endpoint(
    property_id: int,
    db: Session = Depends(get_db),
):
    images = get_images_for_property(
        db=db,
        property_id=property_id,
    )

    return images

@router.get(
    "/admin/all",
    response_model=PropertySearchResponse,
)
def get_all_properties_admin(
    owner_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("admin")
    ),
):
    service = PropertyService(db)

    return service.search_properties(
        owner_id=owner_id,
    )

@router.patch(
    "/{property_id}/owner",
    response_model=PropertyResponse,
)
def update_property_owner(
    property_id: int,
    owner_data: PropertyOwnerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("admin")
    ),
):
    service = PropertyService(db)

    property_obj = service.get_property(property_id)

    if property_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    owner = db.get(User, owner_data.owner_id)

    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner user not found",
        )

    if owner.role not in ("dealer", "admin"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Property owner must be a dealer or admin",
        )

    return service.update_property_owner(
        property_obj,
        owner_data.owner_id,
    )
    
@router.get(
    "/admin/stats",
    response_model=PropertyStatsResponse,
)
def get_property_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("admin")
    ),
):
    service = PropertyService(db)

    return service.get_property_stats()


@router.post("/rag-search")
def rag_search(
    request: RAGSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RAGService(db)

    answer = service.ask(
        query=request.query,
        limit=request.limit,
    )

    return {
        "query": request.query,
        "answer": answer,
    }

@router.get(
    "/{property_id}",
    response_model=PropertyResponse,
)
def get_property(
    property_id: int,
    db: Session = Depends(get_db),
):
    service = PropertyService(db)

    property_obj = service.get_property(property_id)

    if property_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    return property_obj

@router.put(
    "/{property_id}",
    response_model=PropertyResponse,
)
def update_property(
    property_id: int,
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("dealer", "admin")
    ),
):
    service = PropertyService(db)

    try:
        property_obj = service.update_property(
            property_id,
            property_data,
            current_user,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )

    if property_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    return property_obj

@router.delete(
    "/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("dealer", "admin")
    ),
):
    service = PropertyService(db)

    try:
        property_obj = service.delete_property(
            property_id,
            current_user,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )

    if property_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    return None

@router.delete(
    "/{property_id}/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_property_image_endpoint(
    property_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("dealer", "admin")
    ),
):
    service = PropertyService(db)

    property_obj = service.get_property(property_id)

    if property_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )

    if (
        current_user.role != "admin"
        and property_obj.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete images from your own properties",
        )

    success = delete_image(
        db=db,
        property_id=property_id,
        image_id=image_id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property image not found",
        )

    return None




