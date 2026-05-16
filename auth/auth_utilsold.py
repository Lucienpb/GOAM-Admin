"""
Authentication Utility Functions for GOAM Admin
Handles:
- Token verification
- Email verification
- Password reset
- User role lookup
- User storage (JSON-based)
"""

import json
import os
import hashlib
import secrets
from datetime import datetime, timedelta

# ========================================================================
# USER DATABASE (JSON FILE)
# ========================================================================

USER_DB_PATH = "goam-admin/data/users.json"

def load_users():
    """Load user database"""
    if not os.path.exists(USER_DB_PATH):
        return {}
    with open(USER_DB_PATH, "r") as f:
        return json.load(f)

def save_users(users):
    """Save user database"""
    with open(USER_DB_PATH, "w") as f:
        json.dump(users, f, indent=4)


# ========================================================================
# PASSWORD HASHING
# ========================================================================

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


# ========================================================================
# TOKEN GENERATION & VERIFICATION
# ========================================================================

TOKEN_STORE = {}  # In-memory token store (can be replaced with Redis)

def generate_token(email: str, purpose: str, expires_minutes=30) -> str:
    """
    Create a secure token for:
    - email_verification
    - password_reset
    """
    token = secrets.token_urlsafe(32)
    TOKEN_STORE[token] = {
        "email": email,
        "purpose": purpose,
        "expires": datetime.now() + timedelta(minutes=expires_minutes)
    }
    return token

def verify_token(token: str, purpose: str):
    """
    Validate token and return email if valid.
    """
    data = TOKEN_STORE.get(token)

    if not data:
        return None

    if data["purpose"] != purpose:
        return None

    if datetime.now() > data["expires"]:
        del TOKEN_STORE[token]
        return None

    return data["email"]


# ========================================================================
# EMAIL VERIFICATION
# ========================================================================

def verify_user_email(email: str):
    """Mark user as verified"""
    users = load_users()

    if email not in users:
        return False

    users[email]["verified"] = True
    save_users(users)
    return True


# ========================================================================
# PASSWORD RESET
# ========================================================================

def reset_password(email: str, new_password: str):
    """Reset user password"""
    users = load_users()

    if email not in users:
        return False, "User not found"

    users[email]["password"] = hash_password(new_password)
    save_users(users)
    return True, "Password updated"


# ========================================================================
# USER ROLE LOOKUP
# ========================================================================

def get_user_role(email: str) -> str:
    """
    Return user role:
    - admin
    - user
    """
    users = load_users()

    if email not in users:
        return "user"

    return users[email].get("role", "user")


# ========================================================================
# USER CREATION (OPTIONAL)
# ========================================================================

def create_user(email: str, password: str, role="user"):
    """Create a new user account"""
    users = load_users()

    if email in users:
        return False, "User already exists"

    users[email] = {
        "password": hash_password(password),
        "verified": False,
        "role": role
    }

    save_users(users)
    return True, "User created"