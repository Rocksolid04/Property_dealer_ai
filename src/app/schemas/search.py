from pydantic import BaseModel, Field


class PropertySearchQuery(BaseModel):
    location: str | None = None
    property_type: str | None = None
    listing_type: str | None = None

    min_price: float | None = None
    max_price: float | None = None

    bedrooms: int | None = None

    search_text: str | None = Field(
        default=None,
        description="Qualitative semantic requirements such as spacious, modern, near metro, family-friendly, etc."
    )
    
class RAGSearchRequest(BaseModel):
    query: str
    limit: int = 5