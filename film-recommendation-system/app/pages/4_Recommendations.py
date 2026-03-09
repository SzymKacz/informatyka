import streamlit as st
from auth.guard import require_login
from utils.ui import movie_grid_paginated
from db.db_connection import get_connection
from services.profile_movies import get_user_rated_movie_ids_with_ratings
from services.recommender_engine import get_hybrid_recommendations


st.set_page_config(page_title="Rekomendacje filmów", page_icon="🎬", layout="wide")


st.markdown("""
    <style>
   
    .header-container {
        background: linear-gradient(90deg, #1f1f1f 0%, #3d0a0a 100%);
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        border-left: 5px solid #e50914; /* Akcent czerwieni Netflixowej */
    }
    .main-title {
        color: white;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #cccccc;
        font-size: 1.1rem;
    }
   
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #e50914;
    }
    </style>
""", unsafe_allow_html=True)

require_login()


st.markdown("""
    <div class="header-container">
        <h1 class="main-title">✨ Inteligentne Dopasowanie</h1>
        <p class="sub-title">Osobisty algorytm filmowy analizuje Twój profil i wybiera najlepsze tytuły.</p>
    </div>
""", unsafe_allow_html=True)

user_id = st.session_state.get("user_id")

conn = get_connection()
rated_data = get_user_rated_movie_ids_with_ratings(conn, int(user_id))
conn.close()
if not rated_data:
    st.info("### 🍿 Czas na Twoje pierwsze oceny!")
    st.write("Twoja lista rekomendacji jest pusta, ponieważ jeszcze nie oceniono żadnego filmu.")
    if st.button("🔍 Odkryj filmy i zacznij oceniać", use_container_width=True):
        st.switch_page("pages/2_Search.py")
    st.stop()
stat_col1, stat_col2, stat_col3 = st.columns([1, 1, 2])

with stat_col1:
    st.metric("Przeanalizowane oceny", len(rated_data))

with stat_col2:
    if rated_data:
        avg = sum(r for _, r in rated_data) / len(rated_data)
        st.metric("Średnia Twoich ocen", f"{avg:.1f} / 5")
with stat_col3:
    with st.expander("🔍 Jak działa Twój profil?"):
        st.markdown("""
        <small>
        Nasz system hybrydowy łączy:<br>
        - <b>Collaborative Filtering:</b> Trendy od osób o podobnym guście.<br>
        - <b>Content-Based:</b> Analiza gatunków i lat Twoich ulubionych filmów.
        </small>
        """, unsafe_allow_html=True)
st.divider()
st.subheader("🔥 Wybrane specjalnie dla Ciebie")
with st.container():
    with st.spinner(" Nasz algorytm przeszukuje bazę filmów..."):
        try:
            recommendations = get_hybrid_recommendations(user_id, rated_data)
            
            if recommendations:
                movie_grid_paginated(
                    movies=recommendations,
                    page_key="auto_recs",
                    force_pagination=True
                )
            else:
                st.warning("Nie znaleźliśmy nowych filmów idealnie pasujących do Twojego profilu. Spróbuj ocenić coś z innego gatunku!")
        except Exception as e:
            st.error("Wystąpił techniczny problem z silnikiem rekomendacji.")
            st.caption(f"Log błędu: {e}")
st.divider()
st.markdown("<p style='text-align: center; color: gray;'>Smart Cinema AI Engine v2.0</p>", unsafe_allow_html=True)