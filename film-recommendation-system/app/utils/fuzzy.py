from difflib import get_close_matches


def fuzzy_search(query, items, limit=10):
    return get_close_matches(query, items, n=limit, cutoff=0.4)
