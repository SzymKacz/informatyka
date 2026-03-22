import streamlit as st
from db.db_connection import get_connection
from services.user_movie_state import get_user_movie_state, upsert_rating, set_watched

st.set_page_config(page_title="Szczegóły filmu", page_icon="🎬", layout="wide")

from auth.guard import require_login
from services.tmdb_client import get_movie_details

require_login()

IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

def fmt_year(date_str: str | None) -> str:
    if not date_str:
        return "—"
    return date_str[:4] if len(date_str) >= 4 else "—"

def fmt_vote(v) -> str:
    return f"{v:.1f}/10" if isinstance(v, (int, float)) else "—"

def fmt_runtime(minutes) -> str:
    return f"{minutes} min" if isinstance(minutes, int) else "—"

top_actions = st.columns([1, 1, 6])
with top_actions[0]:
    if st.button("⬅ Wróć", use_container_width=True):
        st.switch_page("pages/2_Search.py")
with top_actions[1]:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")

st.title("🎬 Szczegóły filmu")

movie_id = st.session_state.get("selected_movie_id")
if not movie_id:
    st.warning("Nie wybrano filmu. Wróć do wyszukiwarki i kliknij „🎬 Szczegóły”.")
    st.stop()

with st.spinner("Pobieram szczegóły filmu z TMDb..."):
    try:
        details = get_movie_details(int(movie_id))
    except Exception as e:
        st.error("Nie udało się pobrać szczegółów filmu z TMDb.")
        st.caption(str(e))
        st.stop()

title = details.get("title") or "Brak tytułu"
original_title = details.get("original_title")
release_date = details.get("release_date")
year = fmt_year(release_date)

poster_path = details.get("poster_path")
overview = details.get("overview")
tagline = details.get("tagline")

genres = details.get("genres") or []
genres_txt = ", ".join(g.get("name", "") for g in genres if g.get("name")) or "—"

runtime_txt = fmt_runtime(details.get("runtime"))
vote_txt = fmt_vote(details.get("vote_average"))
homepage = details.get("homepage")

left, right = st.columns([1, 2], gap="large")

with left:
    if poster_path:
        st.image(IMAGE_BASE + poster_path, use_container_width=True)
    else:
        st.info("Brak plakatu")

    if homepage:
        st.link_button("🌐 Oficjalna strona", homepage, use_container_width=True)

with right:
    st.markdown(f"## {title} ({year})")

    if original_title and original_title != title:
        st.caption(f"Tytuł oryginalny: {original_title}")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Ocena TMDb", vote_txt)
    with m2:
        st.metric("Czas trwania", runtime_txt)
    with m3:
        st.metric("Gatunki", genres_txt)

    if tagline:
        st.markdown(f"> *{tagline}*")

    st.divider()


    def stars(n: int) -> str:
        return "⭐" * n

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("Brak user_id w sesji. Zaloguj się ponownie.")
        st.stop()

    conn = get_connection()
    state = get_user_movie_state(conn, int(user_id), int(movie_id))

    st.divider()
    st.subheader("Twoje")

    with st.form(f"user_state_{movie_id}", clear_on_submit=False):

        st.markdown(
            """
            <div style="
                padding: 14px 14px 8px 14px;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px;
                background: rgba(255,255,255,0.03);
                margin-bottom: 10px;">
            """,
            unsafe_allow_html=True
        )

        watched_val = st.toggle("Obejrzane", value=state.watched)


        st.markdown("</div>", unsafe_allow_html=True)

        options = [0, 1, 2, 3, 4, 5]
        current = state.rating if state.rating in options else 0

        labels = {
            0: "Brak oceny",
            1: "⭐",
            2: "⭐⭐",
            3: "⭐⭐⭐",
            4: "⭐⭐⭐⭐",
            5: "⭐⭐⭐⭐⭐",
        }

        rating_choice = st.radio(
            "Ocena",
            options=options,
            index=options.index(current),
            format_func=lambda x: labels[x],
            horizontal=True,
            label_visibility="visible",
        )
        rating_val = int(rating_choice)

        c1, c2 = st.columns(2)
        with c1:
            save = st.form_submit_button("💾 Zapisz", use_container_width=True)
        with c2:
            remove_rating = st.form_submit_button("🧹 Usuń ocenę", use_container_width=True)

        if save:
            set_watched(conn, int(user_id), int(movie_id), watched_val)
            upsert_rating(conn, int(user_id), int(movie_id),
                          None if rating_val == 0 else int(rating_val))

            conn.commit()
            conn.close()

            st.success("Zapisano ✅")
            st.rerun()

        if remove_rating:
            upsert_rating(conn, int(user_id), int(movie_id), None)

            conn.commit()
            conn.close()

            st.success("Ocena usunięta ✅")
            st.rerun()

    st.subheader("Opis")
    if overview:
        st.write(overview)
    else:
        st.info("Brak opisu w TMDb (PL).")

st.divider()

bottom = st.columns([1, 1, 4])
with bottom[0]:
    if st.button("⬅ Wróć do wyszukiwarki", use_container_width=True):
        st.switch_page("pages/2_Search.py")
with bottom[1]:
    if st.button("✨ Rekomendacje", use_container_width=True):
        st.switch_page("pages/4_Recommendations.py")
