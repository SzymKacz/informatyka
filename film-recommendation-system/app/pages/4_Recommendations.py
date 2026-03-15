import streamlit as st
from auth.guard import require_login
from utils.ui import movie_grid_paginated
from db.db_connection import get_connection
from services.profile_movies import get_user_rated_movie_ids_with_ratings
from services.recommender_engine import get_hybrid_recommendations

st.set_page_config(page_title=" Movie Recommender", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    
    .main { background-color: #0e1117; }
    
    
    .section-header {
        border-left: 5px solid #00d4ff;
        padding-left: 15px;
        margin-top: 40px;
        margin-bottom: 5px;
        font-size: 1.8rem;
        font-weight: 800;
        color: white;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
    }
    
    
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        border: 1px solid #30363d;
        border-radius: 20px;
        padding: 15px;
        transition: transform 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #00d4ff;
    }

    
    .ai-badge {
        background: linear-gradient(90deg, #ff00c8, #00d4ff);
        color: white;
        padding: 5px 15px;
        border-radius: 50px;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: bold;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
    }

    
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #00d4ff, #ff00c8);
    }
    </style>
""", unsafe_allow_html=True)

require_login()

st.markdown('<p align="right"><span class="ai-badge">Hybrid Engine v2.1 Active</span></p>', unsafe_allow_html=True)
st.title(" Inteligentny System Rekomendacji")
st.markdown("_Algorytm analizuje Twoje oceny oraz metadane z **TMDb** i **MovieLens**, aby przewidzieć Twój gust._")

user_id = st.session_state.get("user_id")
conn = get_connection()
rated_data = get_user_rated_movie_ids_with_ratings(conn, int(user_id))
conn.close()

if not rated_data:
    st.info("###  Brak paliwa dla algorytmu")
    st.write("Oceń kilka filmów, aby uruchomić Collaborative Filtering i Content-Based Filtering.")
    st.stop()


with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Twój Profil", f"{len(rated_data)} ocen", "Aktywny")
    with c2:
        st.metric("Model Content-Based", "TMDb", "100% Online")
    with c3:
        st.metric("Model Collaborative", "SVD", "Wytrenowany")

st.markdown("---")


with st.spinner(" Dobieranie filmów do Twojego profilu w toku ....."):
    
    recommendations = get_hybrid_recommendations(user_id, rated_data, top_n=30)

if recommendations:
    
    st.markdown('<div class="section-header"> Wybrane dla Ciebie</div>', unsafe_allow_html=True)
    st.caption("Filmy o najwyższym przewidywanym dopasowaniu przez model hybrydowy.")
    
    movie_grid_paginated(
        movies=recommendations[:20],
        page_key="hybrid_top",
        force_pagination=False
    )

    st.markdown('<div class="section-header">🔍 Odkrywaj podobne</div>', unsafe_allow_html=True)
    st.caption("Filmy podobne do tych, które już polubiłeś – na podstawie analizy treści.")
    
    movie_grid_paginated(
        movies=recommendations[10:25],
        page_key="content_discovery",
        force_pagination=True
    )
else:
    st.error("Silnik napotkał trudności przy generowaniu rekomendacji. Spróbuj ocenić więcej filmów!")