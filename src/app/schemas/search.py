from pydantic import BaseModel, Field


class PropertySearchQuery(BaseModel):
    location: str | None = None
    property_type: str | None = None
    listing_type: str | None = None

    min_price: float | None = None
    max_price: float | None = None

    bedrooms: int | None = None

    search_text: str = Field(
        default="",
        description="Qualitative semantic requirements such as spacious, modern, near metro, family-friendly, etc."
    )