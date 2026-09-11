def normalize_property(raw_property: dict) -> dict:
    """
    Convert raw 99acres data into the application's
    internal property format.
    """

    if not isinstance(raw_property, dict):
        raise TypeError(
            "Raw property must be a dictionary"
        )

    # ---------------------------------------------------------
    # Basic fields
    # ---------------------------------------------------------

    title = raw_property.get("title")
    external_id = raw_property.get("spid")
    property_type = raw_property.get("propertyType")
    listing_type = raw_property.get("transactionType")

    location = (
        raw_property.get("locality")
        or raw_property.get("city")
    )

    price = raw_property.get("priceInr")
    area_sqft = raw_property.get("areaSqft")

    # ---------------------------------------------------------
    # Required fields
    # ---------------------------------------------------------

    if not external_id:
        raise ValueError(
            "Property external_id is missing"
        )

    if not title:
        raise ValueError(
            "Property title is missing"
        )

    if not property_type:
        raise ValueError(
            "Property type is missing"
        )

    if not listing_type:
        raise ValueError(
            "Listing type is missing"
        )

    if not location:
        raise ValueError(
            "Property location is missing"
        )

    # ---------------------------------------------------------
    # Normalize text fields
    # ---------------------------------------------------------

    external_id = str(external_id).strip()
    title = str(title).strip()
    property_type = str(property_type).strip().lower()
    listing_type = str(listing_type).strip().lower()
    location = str(location).strip()

    if not external_id:
        raise ValueError(
            "Property external_id is empty"
        )

    if not title:
        raise ValueError(
            "Property title is empty"
        )

    if not property_type:
        raise ValueError(
            "Property type is empty"
        )

    if not listing_type:
        raise ValueError(
            "Listing type is empty"
        )

    if not location:
        raise ValueError(
            "Property location is empty"
        )

    # ---------------------------------------------------------
    # Normalize price
    # ---------------------------------------------------------

    if price is None:

        price_min = raw_property.get(
            "priceMinInr"
        )

        price_max = raw_property.get(
            "priceMaxInr"
        )

        if (
            price_min is not None
            and price_max is not None
        ):
            try:
                price = (
                    float(price_min)
                    + float(price_max)
                ) / 2

            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "Property price range contains "
                    "invalid numeric values"
                ) from exc

        elif price_min is not None:
            price = price_min

        elif price_max is not None:
            price = price_max

        else:
            raise ValueError(
                "Property price is missing"
            )

    # ---------------------------------------------------------
    # Area
    # ---------------------------------------------------------

    if area_sqft is None:
        raise ValueError(
            "Property area is missing"
        )

    # ---------------------------------------------------------
    # Numeric validation
    # ---------------------------------------------------------

    try:
        price = float(price)
        area_sqft = float(area_sqft)

    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Price or area contains an invalid "
            "numeric value"
        ) from exc

    if price <= 0:
        raise ValueError(
            "Property price must be greater than 0"
        )

    if area_sqft <= 0:
        raise ValueError(
            "Property area must be greater than 0"
        )

    # ---------------------------------------------------------
    # Bedrooms
    # ---------------------------------------------------------

    bedrooms = raw_property.get(
        "bedrooms"
    )

    if bedrooms is not None:

        try:
            bedrooms = int(bedrooms)

        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Bedrooms contains an invalid value"
            ) from exc

        if bedrooms < 0:
            raise ValueError(
                "Bedrooms cannot be negative"
            )

    # ---------------------------------------------------------
    # Bathrooms
    # ---------------------------------------------------------

    bathrooms = raw_property.get(
        "bathrooms"
    )

    if bathrooms is not None:

        try:
            bathrooms = int(bathrooms)

        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Bathrooms contains an invalid value"
            ) from exc

        if bathrooms < 0:
            raise ValueError(
                "Bathrooms cannot be negative"
            )

    # ---------------------------------------------------------
    # Description
    # ---------------------------------------------------------

    description = raw_property.get(
        "description"
    )

    if description is not None:
        description = str(description).strip()

        if not description:
            description = None

    # ---------------------------------------------------------
    # Final normalized property
    # ---------------------------------------------------------

    return {
        "external_id": external_id,
        "title": title,
        "description": description,
        "property_type": property_type,
        "listing_type": listing_type,
        "location": location,
        "price": price,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "area_sqft": area_sqft,
    }