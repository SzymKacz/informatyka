import requests
import time

BASE_URL = "https://api.imdbapi.dev"
SLEEP_TIME = 0.5


def get_title(imdb_id: str) -> dict | None:
    url = f"{BASE_URL}/title/{imdb_id}"

    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        return None

    time.sleep(SLEEP_TIME)
    return response.json()
