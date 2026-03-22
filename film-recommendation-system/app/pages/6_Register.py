import streamlit as st
from auth.auth import register_user
from db.db import get_user

st.set_page_config(page_title="Rejestracja", page_icon="📝", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

from auth.sidebar import hide_sidebar_nav_for_guests
hide_sidebar_nav_for_guests()

if st.session_state.logged_in:
    st.success(f"Jesteś już zalogowany jako **{st.session_state.username}** ✅")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Przejdź do wyszukiwarki 🔍", type="primary"):
            st.switch_page("pages/2_Search.py")
    with col_b:
        if st.button("Wyloguj"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_id = None
            st.rerun()
    st.stop()

st.title("📝 Rejestracja")
st.caption("Utwórz konto w naszym serwisie")

MIN_USERNAME_LEN = 6
MIN_PASSWORD_LEN = 11

with st.form("register_form", clear_on_submit=True):
    username = st.text_input("Login", key="reg_username")
    password = st.text_input("Hasło", type="password", key="reg_password")

    st.markdown(
        f"""
        <div style="color:#666; font-size:14px; margin-top:6px;">
        • Login: min. <b>{MIN_USERNAME_LEN}</b> znaków<br/>
        • Hasło: min. <b>{MIN_PASSWORD_LEN}</b> znaków
        </div>
        """,
        unsafe_allow_html=True
    )

    submitted = st.form_submit_button("Zarejestruj", use_container_width=True)

if submitted:
    if not username or not password:
        st.error("Proszę wypełnić wszystkie pola.")
    elif len(username) < MIN_USERNAME_LEN:
        st.error(f"Login musi mieć co najmniej {MIN_USERNAME_LEN} znaków.")
    elif len(password) < MIN_PASSWORD_LEN:
        st.error(f"Hasło musi mieć co najmniej {MIN_PASSWORD_LEN} znaków.")
    else:
        if register_user(username, password):
            u = get_user(username)
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_id = int(u["id"]) if u is not None else None
            st.switch_page("pages/2_Search.py")
        else:
            st.error("Użytkownik już istnieje.")

st.divider()

c1, c2 = st.columns([1, 1])
with c1:
    st.write("Masz już konto?")
with c2:
    if st.button("Przejdź do logowania", use_container_width=True):
        st.switch_page("pages/1_Login.py")
