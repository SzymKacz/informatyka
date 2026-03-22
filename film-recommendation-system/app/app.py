import streamlit as st

from services.tmdb_client import get_popular_movies
from utils.ui import movie_grid_paginated

st.set_page_config(
    page_title="Film Recommendation System",
    page_icon="🎬",
    layout="wide"
)

def init_auth_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None

init_auth_state()

from auth.sidebar import hide_sidebar_nav_for_guests
hide_sidebar_nav_for_guests()

def hide_pages_for_guests():
    if not st.session_state.get("logged_in"):
        st.markdown(
            """
            <style>
            /* Ukryj linki do stron (w sidebarze) */
            [data-testid="stSidebarNav"] a[href*="2_Search"] {display:none !important;}
            [data-testid="stSidebarNav"] a[href*="3_Movie_Details"] {display:none !important;}
            [data-testid="stSidebarNav"] a[href*="4_Recommendations"] {display:none !important;}
            [data-testid="stSidebarNav"] a[href*="5_Profile"] {display:none !important;}
            </style>
            """,
            unsafe_allow_html=True
        )

hide_pages_for_guests()


def main():
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown(
            """
            <h1 style="margin-bottom:0;">🎬 Film Recommendation System</h1>
            <p style="font-size:18px; color: #555;">
                Inteligentny system rekomendacji filmów oparty na analizie preferencji użytkownika
                oraz danych o treści filmów.
            </p>
            """,
            unsafe_allow_html=True
        )

    with col_right:
        if st.session_state.logged_in:
            st.success(f"Zalogowano ✅\n\n**{st.session_state.username}**")
            if st.button("Wyloguj"):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.rerun()
        else:
            st.info("Nie jesteś zalogowany")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Logowanie"):
                    st.switch_page("pages/1_Login.py")
            with c2:
                if st.button("Rejestracja"):
                    st.switch_page("pages/6_Register.py")

    st.divider()

    st.markdown(
        """
        <h2>🇵🇱 TOP 5 popularnych filmów w Polsce</h2>
        <p style="color:#666;">
            Najczęściej oglądane filmy według aktualnych danych TMDb
        </p>
        """,
        unsafe_allow_html=True
    )

    data = get_popular_movies(page=1)
    movies = data.get("results", [])[:5]

    if movies:
        movie_grid_paginated(
            movies=movies,
            page_key="top_pl",
            columns=5,
            page_size=5,
            force_pagination=False
        )
    else:
        st.info("Brak danych do wyświetlenia.")

    st.divider()

    st.markdown("<div style='text-align:center; padding: 20px 0;'><h3>🔍 Odkrywaj filmy dopasowane do Ciebie</h3></div>",
                unsafe_allow_html=True)

    if st.button("Przejdź do wyszukiwarki"):
        if st.session_state.logged_in:
            st.switch_page("pages/2_Search.py")
        else:
            st.switch_page("pages/1_Login.py")


if __name__ == "__main__":
    main()
