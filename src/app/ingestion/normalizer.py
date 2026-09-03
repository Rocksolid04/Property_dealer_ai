def normalize_property(raw_property: dict) -> dict:
    """
    Convert raw 99acres data into the application's
    internal property format.
    """

    title = raw_property.get("title")
    external_id = raw_property.get("spid")
    property_type = raw_property.get("propertyType")
    listing_type = raw_property.get("transactionType")
    location = raw_property.get("locality") or raw_property.get("city")
    price = raw_property.get("priceInr")
    area_sqft = raw_property.get("areaSqft")

    # Required fields
    if not title:
        raise ValueError("Property title is missing")

    if not property_type:
        raise ValueError("Property type is missing")

    if not listing_type:
        raise ValueError("Listing type is missing")

    if not location:
        raise ValueError("Property location is missing")

    if price is None:
        raise ValueError("Property price is missing")

    if area_sqft is None:
        raise ValueError("Property area is missing")

    # Normalize numeric values
    try:
        price = float(price)
        area_sqft = float(area_sqft)
    except (TypeError, ValueError) as exc:
        raise ValueError("Price or area contains an invalid numeric value") from exc

    bedrooms = raw_property.get("bedrooms")
    bathrooms = raw_property.get("bathrooms")

    if bedrooms is not None:
        bedrooms = int(bedrooms)

    if bathrooms is not None:
        bathrooms = int(bathrooms)

    return {
        "external_id": external_id,
        "title": title,
        "description": raw_property.get("description"),
        "property_type": property_type,
        "listing_type": listing_type,
        "location": location,
        "price": price,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "area_sqft": area_sqft,
    }