import os
import requests


TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

def search_movies(query: str, page: int = 1):
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "page": page,
        "include_adult": False,
        "language": "pl-PL"
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def get_movie_details(movie_id: int):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "pl-PL"
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def get_popular_people(page: int = 1):
    url = f"{BASE_URL}/person/popular"
    params = {
        "api_key": TMDB_API_KEY,
        "page": page,
        "language": "pl-PL"
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def get_popular_movies(page: int = 1):
    url = f"{BASE_URL}/movie/popular"
    params = {
        "api_key": TMDB_API_KEY,
        "page": page,
        "language": "pl-PL"
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def get_movie_recommendations_tmdb(movie_id: int):
    url = f"{BASE_URL}/movie/{movie_id}/recommendations"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "pl-PL"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"results": []}
    except Exception:
        return {"results": []}

def get_genres():
    url = f"{BASE_URL}/genre/movie/list"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "pl-PL"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        return {g['id']: g['name'] for g in data.get('genres', [])}
    except Exception:
        return {}