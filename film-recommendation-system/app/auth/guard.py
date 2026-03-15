import streamlit as st

def require_login():
    if not st.session_state.get("logged_in"):
        st.warning("Musisz się zalogować, aby uzyskać dostęp do tej strony.")
        st.switch_page("pages/1_Login.py")
        st.stop()
