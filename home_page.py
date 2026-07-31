import streamlit as st

# Navigation function
def navigate_to_page(page_name):
    st.session_state["current_page"] = page_name
    st.rerun()
def home_page():

    st.markdown(
    """
    <div style="text-align: center; padding: 5px; background-color: #333; border-radius: 10px;">
        <h2 style="color: white;">Digital Image Forgery Detection using Combined Texture and Colour Analysis</h2>
    </div>
    """,
    unsafe_allow_html=True
)

    #add image
    st.markdown(
        """
        <div style="text-align: center;">
            <img src="https://www.pngall.com/wp-content/uploads/5/Digital-Marketing-PNG-Transparent-HD-Photo.png" width="400" height="350">
        </div>
        """,
        unsafe_allow_html=True
    )

    # Custom button style with colors
    button_style = """
        <style>
        /* General button style */
        .stButton>button {
            background-color: #4CAF50; /* Default green color */
            color: white;
            font-size: 16px;
            border-radius: 5px;
            padding: 10px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #45a049; /* Darker green for hover */
        }

        /* Specific style for Login button */
        .login-btn>button {
            background-color: #008CBA !important; /* Blue for Login */
        }
        .login-btn>button:hover {
            background-color: #007B9E !important; /* Darker blue for hover */
        }

        /* Specific style for Sign Up button */
        .signup-btn>button {
            background-color: #f44336 !important; /* Red for Sign Up */
        }
        .signup-btn>button:hover {
            background-color: #da190b !important; /* Darker red for hover */
        }
        </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)

    # Layout with columns
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])

    with col2:
        if st.button("Login", key="login_button", help="Click to login", use_container_width=True,type="primary"):
            navigate_to_page("login")

    with col5:
        if st.button("Sign Up", key="signup_button", help="Click to sign up", use_container_width=True,type="primary"):
            navigate_to_page("signup")

