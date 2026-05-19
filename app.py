#-------------------------------
#    """
#    The code is a Streamlit web application for a golf organization's admin tasks, including
#    authentication, user roles, dashboard display, pairing matrix, handicap scraper, scores management,
#    user management, data manager, and profile pages.
#    """
# GOAM ADMIN APP
#-------------------------------
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
from datetime import datetime, timedelta

# AUTH MODULES
from auth.auth import verify_token, verify_user_email, reset_password, get_user_role
from auth.login_page import show_login_page
from auth.profile_page import show_profile_page
from auth.admin_page import show_admin_page

# GOAM MODULES
from apps.pairing_app import run as run_pairing_app
from apps.handicap_app import run as run_handicap_app
from apps.scores_app import run_scores_app
from utils.handicap_calculator import load_course_data
from utils.handicap_scraper import test_login

SESSION_TIMEOUT = 3600  # 1 hour

# ========================================================================
# CONFIG
# ========================================================================
st.set_page_config(
    page_title="GOAM Admin",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================================================
# THEME
# ========================================================================
def inject_theme():
    st.markdown("""
        <style>
        html, body, [class*="css"]  {
            font-family: 'Segoe UI', sans-serif;
        }
        .main {
            background-color: #f7f9fc;
        }
        section[data-testid="stSidebar"] {
            background-color: #D6ECFF; /* Soft Light Blue */
            color: #003366; /* Dark text for contrast */
        }
        section[data-testid="stSidebar"] {
            background-color: #0b3d91;
            color: white;
        }
        .stButton>button {
            background-color: #0b3d91;
            color: white;
            border-radius: 6px;
            padding: 0.6rem 1rem;
            border: none;
            font-weight: 600;
        }
        .stButton>button:hover {
            background-color: #0a357f;
            color: #e6e6e6;
        }
        .stTextInput>div>div>input {
            border-radius: 6px;
            border: 1px solid #c7c7c7;
        }
        div[data-testid="metric-container"] {
            background-color: white;
            padding: 15px 20px;
            border-radius: 10px;
            border: 1px solid #e3e3e3;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }
        .streamlit-expanderHeader {
            font-size: 1.1rem;
            font-weight: 600;
            color: #0b3d91;
        }
        </style>
    """, unsafe_allow_html=True)

inject_theme()

# ========================================================================
# SIDEBAR LOGO
# ========================================================================
st.sidebar.image("assets/goam_logo.png", width='stretch')
st.sidebar.markdown("---")

# ========================================================================
# SESSION INITIALIZATION
# ========================================================================
def init_session():
    defaults = {
        "authenticated": False,
        "email": None,
        "role": None,
        "login_time": None,
        "last_activity": datetime.now(),
        "course_df": None,
        "scrape_cache": {},
        "players_df": None,
        "credentials": {"username": None, "password": None}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session()

# ========================================================================
# SESSION TIMEOUT (FIXED)
# ========================================================================
def check_timeout():
    if not st.session_state.get("authenticated"):
        return

    last = st.session_state.get("last_activity")

    # Fix: initialize if missing
    if last is None:
        st.session_state["last_activity"] = datetime.now()
        return

    # Fix: convert string timestamps
    if isinstance(last, str):
        try:
            last = datetime.fromisoformat(last)
        except:
            st.session_state["last_activity"] = datetime.now()
            return

    # Timeout check
    if datetime.now() - last > timedelta(seconds=SESSION_TIMEOUT):
        st.warning("Session expired. Please login again.")
        st.session_state.authenticated = False
        st.session_state.email = None
        st.session_state.role = None
        st.session_state.login_time = None
        st.session_state.last_activity = None
        st.rerun()

    # Update activity timestamp
    st.session_state.last_activity = datetime.now()

check_timeout()

# ========================================================================
# EMAIL VERIFICATION
# ========================================================================
def handle_email_verification():
    params = st.query_params
    if "token" in params:
        email = verify_token(params["token"], "email_verification")
        if email:
            verify_user_email(email)
            st.success("Email verified successfully! You can now login.")
        else:
            st.error("Invalid or expired verification link.")

handle_email_verification()

# ========================================================================
# PASSWORD RESET
# ========================================================================
def handle_password_reset():
    params = st.query_params
    if "reset-password" in params:
        token = params["token"]
        email = verify_token(token, "password_reset")

        if not email:
            st.error("Invalid or expired reset link.")
            return

        st.header("🔐 Reset Password")
        new_pw = st.text_input("New Password", type="password")
        confirm_pw = st.text_input("Confirm Password", type="password")

        if st.button("Set New Password", use_container_width=True):
            if not new_pw:
                st.error("Password required")
            elif new_pw != confirm_pw:
                st.error("Passwords do not match")
            elif len(new_pw) < 8:
                st.error("Password must be at least 8 characters")
            else:
                ok, msg = reset_password(email, new_pw)
                if ok:
                    st.success("Password reset successful!")
                else:
                    st.error(msg)

        st.stop()

handle_password_reset()

# ========================================================================
# MAIN ROUTING
# ========================================================================
if not st.session_state.authenticated:
    show_login_page()
    st.stop()

# ========================================================================
# SIDEBAR NAVIGATION (NESTED MENU)
# ========================================================================
# ========================================================================
# SIDEBAR NAVIGATION (COMPATIBLE WITH ALL STREAMLIT VERSIONS)
# ========================================================================
st.sidebar.title(f"👤 {st.session_state.email}")
role = get_user_role(st.session_state.email)

main_menu = st.sidebar.radio("Main Menu", [
    "Dashboard",
    "Pairing",
    "Handicap Scraper",
    "GOAM Scores & Rounds",
    "GOAM Season Dashboard",
    "My Profile",
    "Admin" if role == "admin" else None,
    "Logout"
])

# Remove None entries
if main_menu is None:
    main_menu = "Dashboard"

# SUBMENU FOR PAIRING
pairing_sub = None
if main_menu == "Pairing":
    pairing_sub = st.sidebar.radio("Pairing Options", [
        "Matrix",
        "Gen. 4 Ball"
    ])

# SUBMENU FOR ADMIN
admin_sub = None
if main_menu == "Admin":
    admin_sub = st.sidebar.radio("Admin Options", [
        "User Management",
        "Data Manager"
    ])


# ========================================================================
# PAGE ROUTING
# ========================================================================
if main_menu == "Dashboard":
    st.header("📊 GOAM Dashboard")

elif main_menu == "Pairing":
    run_pairing_app()

elif main_menu == "Handicap Scraper":
    username = st.sidebar.text_input("Membership Number", type="password")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login to Handicap System"):
        ok = test_login(username, password)
        if ok:
            st.sidebar.success("Logged in!")
        else:
            st.sidebar.error("Login failed.")
    st.session_state.course_df = load_course_data()
    run_handicap_app(True, st.session_state.credentials, st.session_state.course_df)

elif main_menu == "GOAM Scores & Rounds":
    run_scores_app()

elif main_menu == "GOAM Season Dashboard":
    from apps.goam_dashboard import run
    run()

elif main_menu == "My Profile":
    show_profile_page(st.session_state.email)

elif main_menu == "Admin":
    if admin_sub == "User Management":
        show_admin_page(st.session_state.email)
    elif admin_sub == "Data Manager":
        show_data_manager_page()

elif main_menu == "Logout":
    st.session_state.authenticated = False
    st.session_state.email = None
    st.session_state.role = None
    st.session_state.login_time = None
    st.session_state.last_activity = None
    st.rerun()
