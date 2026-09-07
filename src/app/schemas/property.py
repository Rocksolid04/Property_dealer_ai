from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PropertyBase(BaseModel):
    title: str
    description: str | None = None
    property_type: str
    listing_type: str
    location: str
    price: float
    bedrooms: int | None = None
    bathrooms: int | None = None
    area_sqft: float | None = None


class PropertyCreate(PropertyBase):
    pass


class PropertyImageResponse(BaseModel):
    id: int
    property_id: int
    image_url: str
    storage_path: str
    display_order: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PropertyResponse(PropertyBase):
    id: int
    created_at: datetime
    owner_id: int | None
    images: list[PropertyImageResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class PropertySearchResponse(BaseModel):
    items: list[PropertyResponse]
    total: int
    page: int
    limit: int
    total_pages: int

class PropertySemanticSearchResponse(BaseModel):
    property: PropertyResponse
    similarity: float


class PropertyAISearchResponse(BaseModel):
    items: list[PropertySemanticSearchResponse]
    total: int
    page: int
    limit: int
    total_pages: int

