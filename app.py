"""
GOAM Admin Dashboard - Main Application
"""
import streamlit as st
import logging
from utils.handicap_scraper import test_login
from utils.handicap_calculator import load_course_data
from apps.pairing_app import run as run_pairing_app
from apps.handicap_app import run as run_handicap_app

# ================================================================================
# LOGGING
# ================================================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================================================================
# PAGE CONFIG
# ================================================================================
st.set_page_config(page_title="GOAM Admin", layout="wide")

# ================================================================================
# SESSION STATE INITIALIZATION
# ================================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "credentials" not in st.session_state:
    st.session_state.credentials = {"username": None, "password": None}
if "course_df" not in st.session_state:
    st.session_state.course_df = None
if "scrape_cache" not in st.session_state:
    st.session_state.scrape_cache = {}
if "players_df" not in st.session_state:
    st.session_state.players_df = None

# ================================================================================
# MAIN TITLE
# ================================================================================
st.title("⛳ GOAM Admin Dashboard")

# ================================================================================
# SIDEBAR - LOGIN & COURSE DATA
# ================================================================================
st.sidebar.header("🔐 Handicap Scraper Login")

username = st.sidebar.text_input("Membership Number", type="password")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if username and password:
        with st.spinner("Logging in..."):
            ok = test_login(username, password)
        if ok:
            st.session_state.logged_in = True
            st.session_state.credentials = {"username": username, "password": password}
            st.sidebar.success("Logged in successfully!")
        else:
            st.sidebar.error("Login failed.")
    else:
        st.sidebar.error("Enter username and password")

st.sidebar.write("---")
st.sidebar.subheader("📊 Course Data")

course_file = st.sidebar.file_uploader("Upload Course_Information.xlsx", type=["xlsx"])
if course_file:
    st.session_state.course_df = load_course_data(uploaded_file=course_file)
else:
    st.session_state.course_df = load_course_data()

course_df = st.session_state.course_df

# ================================================================================
# MAIN TABS
# ================================================================================
tab1, tab2 = st.tabs(["⛳ Pairing Matrix & Fourball", "🏌️ Handicap Scraper"])

with tab1:
    run_pairing_app()

with tab2:
    run_handicap_app(st.session_state.logged_in, st.session_state.credentials, course_df)
