from app.database.connection import SessionLocal
from app.ingestion.service import ingest_properties


def main():
    db = SessionLocal()

    try:
        inserted = ingest_properties(
            db=db,
            city="Mumbai",
            transaction_type="buy",
            max_results=20,
        )

        print(f"Successfully ingested {inserted} properties")

    finally:
        db.close()


if __name__ == "__main__":
    main()