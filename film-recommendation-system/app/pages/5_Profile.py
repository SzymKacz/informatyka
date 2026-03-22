import streamlit as st

from auth.guard import require_login
from auth.sidebar import hide_sidebar_nav_for_guests
from auth.auth import check_password, hash_password
from db.db import get_user
from db.db_connection import get_connection
from services.profile_movies import get_user_watched_movie_ids, get_user_rated_movie_ids
from services.tmdb_client import get_movie_details
from utils.ui import movie_grid_paginated

try:
    from db.db import update_user_password
except Exception:
    update_user_password = None

st.set_page_config(page_title="Profil", page_icon="👤", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

hide_sidebar_nav_for_guests()
require_login()

st.title("👤 Profil użytkownika")

user_id = st.session_state.get("user_id")
username = st.session_state.username

if not user_id or not username:
    st.warning("Brak danych sesji. Zaloguj się ponownie.")
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_id = None
    st.switch_page("pages/1_Login.py")
    st.stop()

user = get_user(username)
if user is None:
    st.error("Nie znaleziono użytkownika w bazie danych. Spróbuj zalogować się ponownie.")
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_id = None
    if st.button("Wróć do logowania"):
        st.switch_page("pages/1_Login.py")
    st.stop()

def fetch_movies_by_ids(ids: list[int], limit: int = 50) -> list[dict]:
    movies = []
    for mid in ids[:limit]:
        try:
            details = get_movie_details(int(mid))
            if details:
                movies.append(details)
        except Exception:
            pass
    return movies

conn = get_connection()
watched_ids = get_user_watched_movie_ids(conn, int(user_id))
rated_ids = get_user_rated_movie_ids(conn, int(user_id))
conn.close()

def dedupe_keep_order(ids: list[int]) -> list[int]:
    seen = set()
    out = []
    for x in ids:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

rated_unique = dedupe_keep_order(rated_ids)
watched_unique = dedupe_keep_order(watched_ids)

top1, top2 = st.columns([3, 1])
with top1:
    st.caption(f"Zalogowano jako: **{username}**")
with top2:
    if st.button("Wyloguj", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_id = None
        st.switch_page("pages/1_Login.py")

st.divider()

tab_rated, tab_watched, tab_settings = st.tabs(["⭐ Ocenione", "✅ Obejrzane", "⚙️ Ustawienia konta"])

with tab_rated:
    st.subheader("⭐ Ocenione filmy")
    if not rated_unique:
        st.info("Nie masz jeszcze ocenionych filmów.")
    else:
        rated_movies = fetch_movies_by_ids(rated_unique, limit=50)
        movie_grid_paginated(
            movies=rated_movies,
            page_key="profile_rated",
            force_pagination=True,
        )

with tab_watched:
    st.subheader("✅ Obejrzane filmy")
    if not watched_unique:
        st.info("Nie masz jeszcze obejrzanych filmów.")
    else:
        watched_movies = fetch_movies_by_ids(watched_unique, limit=50)
        movie_grid_paginated(
            movies=watched_movies,
            page_key="profile_watched",
            force_pagination=True,
        )

with tab_settings:
    st.subheader("Twoje konto")
    st.write(f"**Login:** `{username}`")

    st.divider()

    st.subheader("🔐 Zmiana hasła")
    st.caption("Podaj aktualne hasło, a następnie ustaw nowe.")

    MIN_PASSWORD_LEN = 11

    if update_user_password is None:
        st.warning(
            "Brakuje funkcji `update_user_password()` w `db/db.py`. "
            "Dodaj ją, aby zmiana hasła działała."
        )

    with st.form("change_password_form", clear_on_submit=True):
        old_password = st.text_input("Aktualne hasło", type="password", key="old_password")
        new_password = st.text_input("Nowe hasło", type="password", key="new_password")
        new_password2 = st.text_input("Powtórz nowe hasło", type="password", key="new_password2")

        submitted = st.form_submit_button("Zmień hasło", use_container_width=True)

    if submitted:
        if update_user_password is None:
            st.error("Nie można zmienić hasła, bo brakuje `update_user_password()` w bazie.")
        elif not old_password or not new_password or not new_password2:
            st.error("Uzupełnij wszystkie pola.")
        elif not check_password(old_password, user["password_hash"]):
            st.error("Aktualne hasło jest nieprawidłowe.")
        elif len(new_password) < MIN_PASSWORD_LEN:
            st.error(f"Nowe hasło musi mieć co najmniej {MIN_PASSWORD_LEN} znaków.")
        elif new_password != new_password2:
            st.error("Nowe hasła nie są identyczne.")
        elif check_password(new_password, user["password_hash"]):
            st.error("Nowe hasło musi być inne niż aktualne.")
        else:
            new_hash = hash_password(new_password)
            update_user_password(username, new_hash)
            st.success("Hasło zostało zmienione ✅")

    st.divider()

    st.subheader("Przejdź do")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔍 Wyszukiwarka", use_container_width=True):
            st.switch_page("pages/2_Search.py")
    with c2:
        if st.button("✨ Rekomendacje", use_container_width=True):
            st.switch_page("pages/4_Recommendations.py")
    with c3:
        if st.button("🏠 Strona główna", use_container_width=True):
            st.switch_page("app.py")