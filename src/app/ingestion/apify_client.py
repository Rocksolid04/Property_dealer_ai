from apify_client import ApifyClient

from app.core.config import settings


ACTOR_ID = "solidcode/99acres-scraper"


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

    run = client.actor(ACTOR_ID).call(run_input=run_input)

    dataset_items = client.dataset(run.default_dataset_id).iterate_items()

    return list(dataset_items)