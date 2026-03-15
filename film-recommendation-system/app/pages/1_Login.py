import streamlit as st
from auth.auth import login_user

st.set_page_config(page_title="Logowanie", page_icon="🔐", layout="wide")

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

from auth.sidebar import hide_sidebar_nav_for_guests
hide_sidebar_nav_for_guests()

if st.session_state.logged_in:
    st.success(f"Zalogowano jako **{st.session_state.username}** ✅")
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

st.title("🔐 Logowanie")
st.caption("Zaloguj się, aby korzystać z wyszukiwarki i rekomendacji.")

with st.form("login_form", clear_on_submit=True):
    username = st.text_input("Login", key="login_username")
    password = st.text_input("Hasło", type="password", key="login_password")
    submitted = st.form_submit_button("Zaloguj", use_container_width=True)

if submitted:
    if not username or not password:
        st.error("Wpisz login i hasło.")
    else:
        user = login_user(username, password)
        if user is not None and not (hasattr(user, "empty") and user.empty):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_id = user["id"]
            st.switch_page("pages/2_Search.py")
        else:
            st.error("Błędny login lub hasło.")

st.divider()

c1, c2 = st.columns([1, 1])
with c1:
    st.write("Nie masz konta?")
with c2:
    if st.button("Załóż konto", use_container_width=True):
        st.switch_page("pages/6_Register.py")
