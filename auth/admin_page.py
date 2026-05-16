"""
Admin User Management Page
"""

import streamlit as st
from datetime import datetime
from auth import (
    create_user, validate_email, reset_password, load_users,
    send_verification_email, store_token, EMAIL_VERIFICATION_TOKEN_EXPIRY
)


def show_admin_page(user_email: str):
    """Display admin user management page"""
    st.header("👨‍💼 User Management")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Create User", "Manage Users", "Reset Password"])
    
    # ===== CREATE USER TAB =====
    with tab1:
        st.subheader("Create New User")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_email = st.text_input("Email Address")
            role = st.selectbox("Role", ["member", "admin"])
        
        with col2:
            new_password = st.text_input("Initial Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Create User", use_container_width=True):
            # Validation
            if not new_email or not new_password:
                st.error("Email and password are required")
            elif not validate_email(new_email):
                st.error("Invalid email format")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif len(new_password) < 8:
                st.error("Password must be at least 8 characters")
            else:
                # Create user
                success, message = create_user(new_email, new_password, role)
                
                if success:
                    # Generate verification token and send email
                    token = secrets.token_urlsafe(32)
                    store_token(token, new_email, "email_verification", EMAIL_VERIFICATION_TOKEN_EXPIRY)
                    
                    verify_url_base = st.secrets.get("BASE_URL", "http://localhost:8501") + "/verify-email"
                    
                    if send_verification_email(new_email, token, verify_url_base):
                        st.success(f"User created! Verification email sent to {new_email}")
                    else:
                        st.warning(f"User created but verification email could not be sent")
                else:
                    st.error(message)
    
    # ===== MANAGE USERS TAB =====
    with tab2:
        st.subheader("Manage Users")
        
        users = load_users()
        
        if not users:
            st.info("No users found")
        else:
            # Display users table
            user_data = []
            for email, data in users.items():
                user_data.append({
                    "Email": email,
                    "Role": data.get("role", "member"),
                    "Verified": "✓" if data.get("verified") else "✗",
                    "Created": data.get("created_at", "N/A")[:10]
                })
            
            st.dataframe(user_data, use_container_width=True, hide_index=True)
            
            # User actions
            st.divider()
            st.subheader("User Actions")
            
            selected_email = st.selectbox("Select User", list(users.keys()), key="user_select")
            
            if selected_email:
                user = users[selected_email]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Delete User", use_container_width=True):
                        del users[selected_email]
                        from auth import save_users, logger
                        save_users(users)
                        logger.info(f"User deleted by {user_email}: {selected_email}")
                        st.success("User deleted")
                        st.rerun()
                
                with col2:
                    if not user.get("verified") and st.button("Verify Email", use_container_width=True):
                        from auth import verify_user_email
                        verify_user_email(selected_email)
                        st.success("Email marked as verified")
                        st.rerun()
                
                with col3:
                    if st.button("Change Role", use_container_width=True):
                        new_role = "admin" if user.get("role") == "member" else "member"
                        user["role"] = new_role
                        from auth import save_users, logger
                        save_users(users)
                        logger.info(f"User role changed by {user_email}: {selected_email} → {new_role}")
                        st.success(f"Role changed to {new_role}")
                        st.rerun()
    
    # ===== RESET PASSWORD TAB =====
    with tab3:
        st.subheader("Reset User Password")
        
        reset_user_email = st.selectbox("Select User", list(load_users().keys()), key="reset_select")
        reset_password_input = st.text_input("New Password", type="password", key="admin_reset_pass")
        reset_confirm_password = st.text_input("Confirm Password", type="password", key="admin_reset_confirm")
        
        if st.button("Reset Password", use_container_width=True):
            if not reset_password_input:
                st.error("Password is required")
            elif reset_password_input != reset_confirm_password:
                st.error("Passwords do not match")
            elif len(reset_password_input) < 8:
                st.error("Password must be at least 8 characters")
            else:
                success, message = reset_password(reset_user_email, reset_password_input)
                if success:
                    st.success(f"Password reset for {reset_user_email}")
                else:
                    st.error(message)


if __name__ == "__main__":
    import secrets
    show_admin_page("admin@example.com")
