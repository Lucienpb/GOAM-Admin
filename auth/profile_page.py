"""
User Profile Page for GOAM Admin
Allows:
- Viewing account details
- Updating profile info
- Changing password
"""

import streamlit as st
from datetime import datetime
from auth.auth import load_users, save_users, hash_password


# ========================================================================
# PROFILE PAGE
# ========================================================================

def show_profile_page(email: str):
    st.title("👤 My Profile")

    users = load_users()

    if email not in users:
        st.error("User not found")
        return

    user = users[email]

    # ====================================================================
    # ACCOUNT OVERVIEW
    # ====================================================================

    st.subheader("Account Information")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Email:** {email}")
        st.write(f"**Role:** {user.get('role', 'user').capitalize()}")
        st.write(f"**Verified:** {'Yes' if user.get('verified') else 'No'}")

    with col2:
        st.write(f"**Account Created:** {user.get('created', 'N/A')}")
        st.write(f"**Last Updated:** {user.get('updated', 'N/A')}")

    st.markdown("---")

    # ====================================================================
    # UPDATE PROFILE DETAILS
    # ====================================================================

    st.subheader("Update Profile Details")

    name = st.text_input("Full Name", value=user.get("name", ""))
    phone = st.text_input("Phone Number", value=user.get("phone", ""))

    if st.button("Save Profile", use_container_width=True):
        user["name"] = name
        user["phone"] = phone
        user["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        users[email] = user
        save_users(users)

        st.success("Profile updated successfully!")
        st.rerun()

    st.markdown("---")

    # ====================================================================
    # CHANGE PASSWORD
    # ====================================================================

    st.subheader("Change Password")

    current_pw = st.text_input("Current Password", type="password")
    new_pw = st.text_input("New Password", type="password")
    confirm_pw = st.text_input("Confirm New Password", type="password")

    if st.button("Update Password", use_container_width=True):
        # Validate current password
        if user["password"] != hash_password(current_pw):
            st.error("Current password is incorrect")
            return

        if not new_pw:
            st.error("New password cannot be empty")
            return

        if new_pw != confirm_pw:
            st.error("New passwords do not match")
            return

        if len(new_pw) < 8:
            st.error("Password must be at least 8 characters")
            return

        # Update password
        user["password"] = hash_password(new_pw)
        user["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        users[email] = user
        save_users(users)

        st.success("Password updated successfully!")
        st.rerun()
