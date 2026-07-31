import streamlit as st
from database import authenticate_user, fetch_user

def navigate_to_page(page_name):
    st.session_state["current_page"] = page_name
    st.rerun()

def login_page():
    # Center the login form using Streamlit form layout
    st.markdown(
    """
    <style>
    /* Apply background image to the main content area */
    .main {
        background-image: url("https://static.vecteezy.com/system/resources/previews/024/348/400/non_2x/white-elegant-texture-background-design-white-wallpaper-design-template-white-simple-background-texture-free-vector.jpg");  
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }
    </style>
    """,
    unsafe_allow_html=True
    )
    with st.form(key="login_form"):
        # Title
        col1,col2=st.columns([10,1])
        col1.title("Login Here!!")
        if col2.form_submit_button("🏠"):
            navigate_to_page("home")

        # Email and Password inputs
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        # Submit button inside the form
        col1,col2,col3=st.columns([1,4,1])
        with col1:
            if st.form_submit_button("Login"):
                if authenticate_user(email, password):
                    email = st.session_state["current_user"]
                    user = fetch_user(email)
                    st.success(f"Welcome back!")
                    navigate_to_page("user_home")
                else:
                    st.error("Invalid Details.")
        with col3:
            if st.form_submit_button("Sign Up🤔"):
                navigate_to_page("signup")