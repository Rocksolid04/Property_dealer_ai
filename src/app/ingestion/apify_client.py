import time

from apify_client import ApifyClient

from app.core.config import settings


ACTOR_ID = "solidcode/99acres-scraper"

MAX_RETRIES = 3
RETRY_DELAYS = [60, 120]


def fetch_properties(
    city: str = "Mumbai",
    transaction_type: str = "buy",
    max_results: int = 5,
):
    client = ApifyClient(settings.APIFY_API_TOKEN)

    run_input = {
        "city": city,
        "transactionType": transaction_type,
        "maxResults": max_results,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(
                f"Starting Apify run "
                f"(attempt {attempt}/{MAX_RETRIES})..."
            )

            run = client.actor(ACTOR_ID).call(
                run_input=run_input
            )

            dataset_items = client.dataset(
                run.default_dataset_id
            ).iterate_items()

            properties = list(dataset_items)

            if properties:
                print(
                    f"Apify run completed. "
                    f"Fetched {len(properties)} properties."
                )
                return properties

            print(
                "Apify run returned 0 properties. "
                "The source may be temporarily blocking requests."
            )

        except Exception as exc:
            print(
                f"Apify attempt {attempt}/{MAX_RETRIES} failed: "
                f"{type(exc).__name__}: {exc}"
            )

        if attempt < MAX_RETRIES:
            delay = RETRY_DELAYS[attempt - 1]

            print(
                f"Waiting {delay} seconds before retry..."
            )

            time.sleep(delay)

    raise RuntimeError(
        f"Apify could not fetch properties for "
        f"{city} - {transaction_type} "
        f"after {MAX_RETRIES} attempts."
    )