# auth.py
import streamlit as st

# Demo credentials
DEMO_EMAIL = "test@example.com"
DEMO_PASSWORD = "123456"

def login_user(supabase_conn):
    """Handles the user login."""
    st.subheader("Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        try:
            result = supabase_conn.auth.sign_in_with_password({
                "email": username,
                "password": password
            })
            st.session_state['authenticated'] = True
            st.session_state['user'] = result.user
            st.success("Login successful")
        except Exception as e:
            st.error(f"Failed to login: {str(e)}")

    # Try the demo account
    if st.button("Try Demo"):
        demo_login(supabase_conn)

def demo_login(supabase_conn):
    """Automatically logs in the user with the demo account."""
    try:
        result = supabase_conn.auth.sign_in_with_password({
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })

        st.session_state['authenticated'] = True
        st.session_state['user'] = result.user
        st.session_state['is_demo'] = True  # Mark that this is a demo user
        st.success("You are now logged in as a demo user!")
    except Exception as e:
        error_message = str(e)
        if "Invalid login credentials" in error_message:
            st.error("Failed to log in with demo account: The demo account may not exist in the database. Please ensure it has been created.")
        elif "Email not confirmed" in error_message:
            st.error("Failed to log in with demo account: The demo account email is not confirmed. Please confirm it in the Supabase dashboard.")
        else:
            st.error(f"Failed to log in with demo account: {error_message}")

def register_user(supabase_conn):
    """Handles the user registration."""
    st.subheader("Register")

    email = st.text_input("Email", key="register_email")
    password = st.text_input("Password", type="password", key="register_password")

    if st.button("Register"):
        try:
            result = supabase_conn.auth.sign_up({
                "email": email,
                "password": password
            })
            st.success("Registration successful. Please log in.")
        except Exception as e:
            st.error(f"Failed to register: {str(e)}")

def authenticate_user(supabase_conn):
    """Checks if a user is authenticated and provides login/registration options."""
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if not st.session_state['authenticated']:
        option = st.selectbox("Login or Register", ["Login", "Register"])

        if option == "Login":
            login_user(supabase_conn)
        else:
            register_user(supabase_conn)
    else:
        if st.session_state.get('is_demo'):
            st.sidebar.info("You are using the demo account.")
        st.sidebar.success(f"Logged in as {st.session_state['user'].email}")