import streamlit as st
from auth.authentication import AuthManager
from auth.email_service import EmailService

# Initialize managers
auth_manager = AuthManager()
email_service = EmailService()


def render_auth():
    """Render authentication page with modern styling"""
    
    # Handle email verification from URL parameters
    query_params = st.query_params
    if 'verify' in query_params and 'email' in query_params:
        verification_token = query_params['verify']
        email = query_params['email']
        
        # Verify the user
        success = auth_manager.verify_email(email, verification_token)
        
        if success:
            st.success("Email verified successfully! You can now login.")
            # Clear query parameters
            st.query_params.clear()
        else:
            st.error("Invalid or expired verification link.")
            st.query_params.clear()
    
    # Center the auth form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>OSCAR</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: rgba(255, 255, 255, 0.5); font-size: 0.9rem; margin-bottom: 3rem; text-transform: uppercase; letter-spacing: 0.2em; font-weight: 400;'>Track. Save. Review.</p>", unsafe_allow_html=True)
        
        # Create tabs for login and register
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            render_login()
        
        with tab2:
            render_register()


def render_login():
    """Render login form"""
    st.markdown("### Sign In")
    
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
        
        if submit:
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                user = auth_manager.login_user(email, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success("Login successful!")
                    st.rerun()
                else:
                    # Check if user exists but is unverified
                    from database.db_manager import DatabaseManager
                    db = DatabaseManager()
                    existing_user = db.get_user_by_email(email)
                    
                    if existing_user and not existing_user['is_verified']:
                        st.error("Please verify your email before logging in. Check your inbox for the verification link.")
                    else:
                        st.error("Invalid email or password")


def render_register():
    """Render registration form"""
    st.markdown("### Create Account")
    
    with st.form("register_form", clear_on_submit=True):
        full_name = st.text_input("Full Name", placeholder="Enter your full name")
        email = st.text_input("Email", placeholder="your.email@example.com")
        password = st.text_input("Password", type="password", placeholder="Create a strong password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
        
        submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")
        
        if submit:
            if not full_name or not email or not password or not confirm_password:
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long")
            elif '@' not in email or '.' not in email:
                st.error("Please enter a valid email address")
            else:
                # Register user
                result = auth_manager.register_user(email, password, full_name)
                
                if result:
                    # Send verification email
                    try:
                        email_sent = email_service.send_verification_email(
                            email,
                            result['verification_token']
                        )
                        if email_sent:
                            st.success("Account created successfully!")
                            st.info("Please check your email to verify your account, then login.")
                        else:
                            st.warning("Account created but couldn't send verification email. Please check your email configuration.")
                            st.info("You may need to contact support for manual verification.")
                    except Exception as e:
                        st.warning(f"Account created but couldn't send verification email. Error: {str(e)}")
                        st.info("Please contact support for manual verification.")
                else:
                    st.error("Email already exists or registration failed. Please try a different email.")