from app.models.properties import Property


def build_property_document(property_obj: Property) -> str:
    """
    Convert a Property database object into a
    natural-language document for embedding and RAG.
    """

    parts = []

    parts.append(
        f"{property_obj.title} in {property_obj.location}."
    )

    parts.append(
        f"Property type: {property_obj.property_type}."
    )

    parts.append(
        f"Listing type: {property_obj.listing_type}."
    )

    parts.append(
        f"Price: ₹{property_obj.price:,.0f}."
    )

    if property_obj.area_sqft is not None:
        parts.append(
            f"Area: {property_obj.area_sqft:,.0f} sq ft."
        )

    if property_obj.bedrooms is not None:
        parts.append(
            f"Bedrooms: {property_obj.bedrooms}."
        )

    if property_obj.bathrooms is not None:
        parts.append(
            f"Bathrooms: {property_obj.bathrooms}."
        )

    if property_obj.description:
        parts.append(
            f"Description: {property_obj.description}"
        )

    return " ".join(parts)