import streamlit as st
from home_page import home_page
from login_page import login_page
from signup_page import signup_page
from user_home_page import user_home_page
st.set_page_config(page_title="Forgery Detection", page_icon=":camera:", layout="centered")

# Initialize session state
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "home"
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
try:
    if st.session_state["current_page"] == "home":
        home_page()
    elif st.session_state["current_page"] == "login":
        login_page()
    elif st.session_state["current_page"] == "signup":
        signup_page()
    elif st.session_state["current_page"] == "user_home":
        user_home_page()
except Exception as e:
    st.error(f"An error occurred: {e}")