import streamlit as st

st.set_page_config(page_title="Search movies", layout="wide")

from auth.guard import require_login
require_login()

from utils.ui import movie_grid_paginated
from services.tmdb_client import search_movies, get_popular_movies

st.set_page_config(
    page_title="Search movies",
    layout="wide"
)

st.title("🔍 Wyszukiwanie filmów")

query = st.text_input(
    "Wyszukaj film",
    placeholder="Zacznij pisać tytuł filmu..."
)

if "last_query" not in st.session_state:
    st.session_state.last_query = ""

if query != st.session_state.last_query:
    st.session_state["search_page"] = 1
    st.session_state.last_query = query

if query and len(query) >= 2:
    data = search_movies(query)
    movies = data.get("results", [])
    st.subheader(f"Wyniki wyszukiwania dla: **{query}**")
    page_key = "search"
    force_pagination = True
else:
    data = get_popular_movies()
    movies = data.get("results", [])
    st.subheader("🔥 Popularne filmy")
    page_key = "popular"
    force_pagination = False

movie_grid_paginated(
    movies=movies,
    page_key=page_key,
    force_pagination=force_pagination
)