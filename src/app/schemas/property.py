from datetime import datetime

from pydantic import BaseModel, ConfigDict


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


class PropertyResponse(PropertyBase):
    id: int | None
    created_at: datetime
    owner_id: int

    model_config = ConfigDict(from_attributes=True)


class PropertySearchResponse(BaseModel):
    items: list[PropertyResponse]
    total: int
    page: int
    limit: int
    total_pages: int

class PropertyImageResponse(BaseModel):
    id: int
    property_id: int
    image_url: str
    storage_path: str
    display_order: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)