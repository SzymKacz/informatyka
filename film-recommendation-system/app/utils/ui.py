# app/utils/ui.py
import streamlit as st

IMAGE_BASE = "https://image.tmdb.org/t/p/w300"


def movie_grid_paginated(
    movies: list,
    page_key: str,
    columns: int = 5,
    page_size: int = 50,
    force_pagination: bool = False,
    poster_width: int = 280,   
    poster_height: int = 370   
):
    if not movies:
        st.info("Brak filmów do wyświetlenia.")
        return

    page_state_key = f"{page_key}_page"
    if page_state_key not in st.session_state:
        st.session_state[page_state_key] = 1

    total = len(movies)
    total_pages = max(1, (total - 1) // page_size + 1)
    show_pagination = force_pagination or total > page_size

    page = st.session_state[page_state_key]
    start = (page - 1) * page_size
    end = start + page_size
    page_movies = movies[start:end]

    rows = [page_movies[i:i + columns] for i in range(0, len(page_movies), columns)]

    for row_movies in rows:
        cols = st.columns(columns)

        for i, movie in enumerate(row_movies):
            col = cols[i]
            with col:
                if movie.get("poster_path"):
                    img_url = IMAGE_BASE + movie["poster_path"]
                    st.markdown(
                        f"""
                        <div style="width:{poster_width}px; height:{poster_height}px; overflow:hidden;">
                            <img src="{img_url}" style="width:100%; height:100%; object-fit:cover;">
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown(f"**{movie.get('title', 'Brak tytułu')}**")
                if movie.get("release_date"):
                    st.caption(movie["release_date"][:4])

                if st.button("🎬 Szczegóły", key=f"{page_key}_movie_{movie['id']}"):
                    st.session_state["selected_movie_id"] = movie["id"]
                    st.switch_page("pages/3_Movie_Details.py")

        st.markdown("<br>", unsafe_allow_html=True)

    if show_pagination:
        st.divider()
        prev, info, next_ = st.columns([1, 2, 1])

        with prev:
            if st.button("⬅ Poprzednia", disabled=page <= 1, key=f"{page_key}_prev"):
                st.session_state[page_state_key] -= 1
                st.rerun()

        with info:
            st.markdown(
                f"<div style='text-align:center'>Strona {page} z {total_pages}</div>",
                unsafe_allow_html=True
            )

        with next_:
            if st.button("Następna ➡", disabled=page >= total_pages, key=f"{page_key}_next"):
                st.session_state[page_state_key] += 1
                st.rerun()
