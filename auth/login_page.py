"""
Login Page with Throttling and Forgot Password
"""

import streamlit as st
from datetime import datetime, timedelta
import json
from pathlib import Path
from auth import (
    authenticate_user, validate_email, send_password_reset_email,
    store_token, PASSWORD_RESET_TOKEN_EXPIRY, user_exists
)


# ========================================================================
# CONFIGURATION
# ========================================================================

THROTTLE_FILE = Path("data/login_throttle.json")
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = 60  # seconds


# ========================================================================
# THROTTLING
# ========================================================================

def _ensure_throttle_file():
    """Ensure throttle file exists"""
    THROTTLE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not THROTTLE_FILE.exists():
        THROTTLE_FILE.write_text(json.dumps({}, indent=2))


def get_login_attempts(email: str) -> dict:
    """Get login attempts for an email"""
    _ensure_throttle_file()
    throttle_data = json.loads(THROTTLE_FILE.read_text())
    return throttle_data.get(email, {"attempts": 0, "locked_until": None})


def record_failed_attempt(email: str):
    """Record a failed login attempt"""
    _ensure_throttle_file()
    throttle_data = json.loads(THROTTLE_FILE.read_text())
    
    attempt_info = throttle_data.get(email, {"attempts": 0, "locked_until": None})
    attempt_info["attempts"] += 1
    
    if attempt_info["attempts"] >= MAX_FAILED_ATTEMPTS:
        attempt_info["locked_until"] = (datetime.now() + timedelta(seconds=LOCKOUT_DURATION)).isoformat()
    
    throttle_data[email] = attempt_info
    THROTTLE_FILE.write_text(json.dumps(throttle_data, indent=2))


def record_successful_login(email: str):
    """Clear throttle data after successful login"""
    _ensure_throttle_file()
    throttle_data = json.loads(THROTTLE_FILE.read_text())
    
    if email in throttle_data:
        del throttle_data[email]
        THROTTLE_FILE.write_text(json.dumps(throttle_data, indent=2))


def is_account_locked(email: str) -> bool:
    """Check if account is locked"""
    attempt_info = get_login_attempts(email)
    
    if attempt_info["locked_until"] is None:
        return False
    
    locked_until = datetime.fromisoformat(attempt_info["locked_until"])
    if datetime.now() < locked_until:
        return True
    
    # Unlock expired lockout
    _ensure_throttle_file()
    throttle_data = json.loads(THROTTLE_FILE.read_text())
    del throttle_data[email]
    THROTTLE_FILE.write_text(json.dumps(throttle_data, indent=2))
    
    return False


def get_lockout_remaining_seconds(email: str) -> int:
    """Get remaining lockout time in seconds"""
    attempt_info = get_login_attempts(email)
    
    if attempt_info["locked_until"] is None:
        return 0
    
    locked_until = datetime.fromisoformat(attempt_info["locked_until"])
    remaining = (locked_until - datetime.now()).total_seconds()
    return max(0, int(remaining))


# ========================================================================
# LOGIN PAGE
# ========================================================================

def show_login_page():
    """Display login page"""
    st.set_page_config(page_title="Login", layout="centered")
    
    st.title("🔐 Secure Login")
    
    # Create tabs for login and forgot password
    tab1, tab2 = st.tabs(["Login", "Forgot Password"])
    
    # ===== LOGIN TAB =====
    with tab1:
        st.subheader("Login to Your Account")
        
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_button", use_container_width=True):
            # Check if account is locked
            if is_account_locked(email):
                remaining = get_lockout_remaining_seconds(email)
                st.error(f"Account locked due to too many failed attempts. Try again in {remaining} seconds.")
            else:
                # Attempt login
                success, message = authenticate_user(email, password)
                
                if success:
                    record_successful_login(email)
                    st.success(message)
                    st.session_state.authenticated = True
                    st.session_state.email = email
                    st.rerun()
                else:
                    record_failed_attempt(email)
                    attempt_info = get_login_attempts(email)
                    
                    st.error(message)
                    
                    if attempt_info["attempts"] >= MAX_FAILED_ATTEMPTS:
                        remaining = get_lockout_remaining_seconds(email)
                        st.warning(f"Account locked. Try again in {remaining} seconds.")
                    else:
                        remaining_attempts = MAX_FAILED_ATTEMPTS - attempt_info["attempts"]
                        st.warning(f"Failed attempts: {attempt_info['attempts']}/{MAX_FAILED_ATTEMPTS}")
                        st.warning(f"Remaining attempts: {remaining_attempts}")
    
    # ===== FORGOT PASSWORD TAB =====
    with tab2:
        st.subheader("Reset Your Password")
        
        reset_email = st.text_input("Enter your email address", key="reset_email")
        
        if st.button("Send Reset Link", key="reset_button", use_container_width=True):
            if not validate_email(reset_email):
                st.error("Invalid email format")
            elif not user_exists(reset_email):
                # Don't reveal if user exists
                st.success("If an account exists with this email, you will receive a password reset link.")
            else:
                # Generate token and send email
                token = secrets.token_urlsafe(32)
                store_token(token, reset_email, "password_reset", PASSWORD_RESET_TOKEN_EXPIRY)
                
                # Build reset URL (adjust as needed for your deployment)
                reset_url_base = st.secrets.get("BASE_URL", "http://localhost:8501") + "/reset-password"
                
                if send_password_reset_email(reset_email, token, reset_url_base):
                    st.success("Password reset link sent! Check your email.")
                else:
                    st.error("Failed to send reset email. Please try again later.")
    
    # Sign up link
    st.divider()
    st.write("Don't have an account? Contact an administrator to create one.")


if __name__ == "__main__":
    import secrets
    show_login_page()
