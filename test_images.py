from app.ingestion.apify_client import fetch_properties


def main():
    properties = fetch_properties(
        city="Mumbai",
        transaction_type="buy",
        max_results=1,
    )

    if not properties:
        print("No properties returned")
        return

    property_data = properties[0]

    print("\nPROPERTY:")
    print(property_data.get("title"))

    print("\nIMAGES:")
    print(property_data.get("propertyImages"))


if __name__ == "__main__":
    main()