"""
User Profile Page - Self-Service Password Change
"""

import streamlit as st
from auth import change_password, get_user_role


def show_profile_page(user_email: str):
    """Display user profile page"""
    st.header("👤 My Profile")
    
    # Display user info
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Email:** {user_email}")
    
    with col2:
        role = get_user_role(user_email)
        st.write(f"**Role:** {role.capitalize()}")
    
    st.divider()
    
    # Change password section
    st.subheader("Change Password")
    
    old_password = st.text_input("Current Password", type="password", key="old_pass")
    new_password = st.text_input("New Password", type="password", key="new_pass")
    confirm_new_password = st.text_input("Confirm New Password", type="password", key="confirm_new_pass")
    
    if st.button("Change Password", use_container_width=True):
        # Validation
        if not old_password or not new_password:
            st.error("All fields are required")
        elif new_password != confirm_new_password:
            st.error("New passwords do not match")
        elif len(new_password) < 8:
            st.error("Password must be at least 8 characters")
        elif old_password == new_password:
            st.error("New password must be different from current password")
        else:
            # Change password
            success, message = change_password(user_email, old_password, new_password)
            
            if success:
                st.success(message)
                st.balloons()
            else:
                st.error(message)
    
    st.divider()
    
    # Session info
    st.subheader("Session Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if "login_time" in st.session_state:
            st.write(f"**Logged in since:** {st.session_state.login_time}")
    
    with col2:
        if st.button("Logout", use_container_width=True, key="profile_logout"):
            st.session_state.authenticated = False
            st.session_state.email = None
            if "login_time" in st.session_state:
                del st.session_state.login_time
            if "last_activity" in st.session_state:
                del st.session_state.last_activity
            st.rerun()


if __name__ == "__main__":
    show_profile_page("user@example.com")
