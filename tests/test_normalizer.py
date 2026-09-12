from app.ingestion.normalizer import normalize_property


property_data = {
    "spid": "J82637930",
    "propertyType": "Residential Land",
    "transactionType": "buy",
    "title": "Residential land / Plot in Uran, Navi Mumbai",
    "bedrooms": None,
    "bathrooms": None,
    "areaSqft": 21780,
    "priceInr": 7500000,
    "priceMinInr": None,
    "priceMaxInr": None,
    "city": "Navi Mumbai",
    "locality": "Uran, Navi Mumbai",
}


result = normalize_property(property_data)

print(result)