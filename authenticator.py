import streamlit as st
from db.user_management import verify_user

def login_screen():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    st.button("Login", on_click= checklogin(username,password))
    """
    if st.button("Login"):
        checklogin(password, username)
    """

def checklogin(password, username):
    user = verify_user(username, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.username = username
    else:
        if username and password:
            st.error("Incorrect username or password")


def logout():
    if st.session_state.logged_in:
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.success("You have successfully logged out!")