import streamlit as st

def hide_sidebar_nav_for_guests():
    if not st.session_state.get("logged_in"):
        st.markdown(
            """
            <style>
            section[data-testid="stSidebar"] { display: none !important; }
            </style>
            """,
            unsafe_allow_html=True
        )
