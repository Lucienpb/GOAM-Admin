"""
Main Streamlit App with Authentication, Routing, and Session Management
"""

import streamlit as st
from datetime import datetime, timedelta
from auth import verify_token, verify_user_email, reset_password, get_user_role
from login_page import show_login_page
from profile_page import show_profile_page
from admin_page import show_admin_page


# ========================================================================
# CONFIGURATION
# ========================================================================

SESSION_TIMEOUT = 30 * 60  # 30 minutes in seconds


# ========================================================================
# SESSION MANAGEMENT
# ========================================================================

def initialize_session():
    """Initialize session state variables"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "email" not in st.session_state:
        st.session_state.email = None
    if "login_time" not in st.session_state:
        st.session_state.login_time = None
    if "last_activity" not in st.session_state:
        st.session_state.last_activity = datetime.now()


def check_session_timeout():
    """Check if session has timed out"""
    if not st.session_state.authenticated:
        return
    
    if st.session_state.last_activity is None:
        st.session_state.last_activity = datetime.now()
        return
    
    # Parse last_activity if it's a string
    if isinstance(st.session_state.last_activity, str):
        last_activity = datetime.fromisoformat(st.session_state.last_activity)
    else:
        last_activity = st.session_state.last_activity
    
    # Check timeout
    if datetime.now() - last_activity > timedelta(seconds=SESSION_TIMEOUT):
        st.session_state.authenticated = False
        st.session_state.email = None
        st.session_state.login_time = None
        st.session_state.last_activity = None
        st.warning("Session expired. Please login again.")
        st.rerun()
    
    # Update last activity
    st.session_state.last_activity = datetime.now()


def require_login(func):
    """Decorator to require login"""
    def wrapper(*args, **kwargs):
        if not st.session_state.authenticated:
            st.error("Please login to access this page")
            st.stop()
        return func(*args, **kwargs)
    return wrapper


def require_admin(func):
    """Decorator to require admin role"""
    def wrapper(*args, **kwargs):
        if not st.session_state.authenticated:
            st.error("Please login to access this page")
            st.stop()
        
        role = get_user_role(st.session_state.email)
        if role != "admin":
            st.error("You do not have permission to access this page")
            st.stop()
        
        return func(*args, **kwargs)
    return wrapper


# ========================================================================
# EMAIL VERIFICATION HANDLER
# ========================================================================

def handle_email_verification():
    """Handle email verification from query parameters"""
    query_params = st.query_params
    
    if "token" in query_params:
        token = query_params["token"]
        email = verify_token(token, "email_verification")
        
        if email:
            verify_user_email(email)
            st.success("✓ Email verified successfully! You can now login.")
        else:
            st.error("Invalid or expired verification link.")


# ========================================================================
# PASSWORD RESET HANDLER
# ========================================================================

def handle_password_reset():
    """Handle password reset from query parameters"""
    query_params = st.query_params
    
    if "token" in query_params:
        token = query_params["token"]
        email = verify_token(token, "password_reset")
        
        if not email:
            st.error("Invalid or expired password reset link.")
            return
        
        st.header("🔐 Reset Password")
        
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Set New Password", use_container_width=True):
            if not new_password:
                st.error("Password is required")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif len(new_password) < 8:
                st.error("Password must be at least 8 characters")
            else:
                success, message = reset_password(email, new_password)
                if success:
                    st.success("Password reset successful! You can now login.")
                    st.session_state.show_reset_form = False
                else:
                    st.error(message)


# ========================================================================
# MAIN APP ROUTING
# ========================================================================

def main():
    """Main application"""
    initialize_session()
    
    # Check for email verification
    handle_email_verification()
    
    # Check for password reset
    if "verify-email" in st.query_params or "reset-password" in st.query_params:
        if "reset-password" in st.query_params:
            handle_password_reset()
        st.stop()
    
    # Check session timeout
    check_session_timeout()
    
    # ===== LOGGED OUT VIEW =====
    if not st.session_state.authenticated:
        show_login_page()
    
    # ===== LOGGED IN VIEW =====
    else:
        # Sidebar navigation
        st.sidebar.title(f"👤 {st.session_state.email}")
        
        role = get_user_role(st.session_state.email)
        page = st.sidebar.radio(
            "Navigation",
            ["Dashboard", "My Profile"] + (["User Management"] if role == "admin" else []) + ["Logout"]
        )
        
        # Session timeout display
        if st.session_state.login_time:
            st.sidebar.write(f"Logged in: {st.session_state.login_time}")
        
        # ===== DASHBOARD PAGE =====
        if page == "Dashboard":
            st.header("📊 Dashboard")
            st.write("Welcome to your dashboard!")
            
            # Display your dashboard content here
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Your Role", role.capitalize())
            with col2:
                st.metric("Account Status", "✓ Verified")
            with col3:
                st.metric("Login Time", st.session_state.login_time[:16] if st.session_state.login_time else "N/A")
        
        # ===== PROFILE PAGE =====
        elif page == "My Profile":
            show_profile_page(st.session_state.email)
        
        # ===== ADMIN PAGE =====
        elif page == "User Management" and role == "admin":
            show_admin_page(st.session_state.email)
        
        # ===== LOGOUT =====
        elif page == "Logout":
            st.session_state.authenticated = False
            st.session_state.email = None
            st.session_state.login_time = None
            st.session_state.last_activity = None
            st.rerun()
        
        # Log first login time
        if not st.session_state.login_time:
            st.session_state.login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    st.set_page_config(
        page_title="Secure Auth System",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    main()