
from app.database.connection import SessionLocal
from app.ingestion.service import ingest_properties


TARGETS = [
    {"city": "Mumbai", "transaction_type": "rent", "target": 150},
    {"city": "Navi Mumbai", "transaction_type": "buy", "target": 150},
    {"city": "Navi Mumbai", "transaction_type": "rent", "target": 150},
    {"city": "Thane", "transaction_type": "buy", "target": 150},
    {"city": "Thane", "transaction_type": "rent", "target": 150},
]

BATCH_SIZE = 50


def main():
    total_inserted = 0

    for target in TARGETS:
        city = target["city"]
        transaction_type = target["transaction_type"]
        target_count = target["target"]

        print(
            f"\n{'=' * 60}\n"
            f"Target: {city} - {transaction_type}\n"
            f"Requested: {target_count} properties\n"
            f"Batch size: {BATCH_SIZE}\n"
            f"{'=' * 60}"
        )

        batches = (
            target_count + BATCH_SIZE - 1
        ) // BATCH_SIZE

        target_inserted = 0

        for batch_number in range(1, batches + 1):
            remaining = target_count - target_inserted
            batch_size = min(BATCH_SIZE, remaining)

            print(
                f"\n--- Batch {batch_number}/{batches} ---"
            )

            print(
                f"Fetching up to {batch_size} "
                f"{transaction_type} properties "
                f"in {city}..."
            )

            db = SessionLocal()

            try:
                inserted = ingest_properties(
                    db=db,
                    city=city,
                    transaction_type=transaction_type,
                    max_results=batch_size,
                )

                target_inserted += inserted
                total_inserted += inserted

                print(
                    f"Batch completed: {inserted} inserted"
                )

                print(
                    f"Progress for {city} {transaction_type}: "
                    f"{target_inserted}/{target_count}"
                )

            except Exception as exc:
                print(
                    f"ERROR in batch {batch_number}: {exc}"
                )

                print(
                    "Stopping ingestion because the "
                    "Apify source may be temporarily blocked."
                )

                db.rollback()
                db.close()

                return

            finally:
                db.close()

        print(
            f"\nCompleted target: "
            f"{city} - {transaction_type}"
        )

        print(
            f"Inserted for this target: "
            f"{target_inserted}/{target_count}"
        )

    print(
        f"\n{'=' * 60}\n"
        f"ALL INGESTION COMPLETED\n"
        f"Total newly inserted: {total_inserted}\n"
        f"{'=' * 60}"
    )


if __name__ == "__main__":
    main()
