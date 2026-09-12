import os

from dotenv import load_dotenv

load_dotenv()


FASTAPI_URL = os.getenv(
    "FASTAPI_URL",
    "http://127.0.0.1:8000/api/v1",
).rstrip("/")