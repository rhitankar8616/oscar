import streamlit as st
from datetime import datetime, date
import config
from database.db_manager import DatabaseManager

def render_profile(user: dict, db: DatabaseManager):
    """Render user profile page"""
    st.markdown("### Profile")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Personal Info", "Financial Settings", "Account"])
    
    with tab1:
        render_personal_info(user, db)
    
    with tab2:
        render_financial_settings(user, db)
    
    with tab3:
        render_account_settings(user, db)

def render_personal_info(user: dict, db: DatabaseManager):
    """Render personal information section"""
    st.markdown("#### Personal Information")
    
    with st.form("personal_info_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input(
                "Full Name",
                value=user.get('full_name', ''),
                placeholder="Enter your full name"
            )
            
            email = st.text_input(
                "Email",
                value=user.get('email', ''),
                disabled=True,
                help="Email cannot be changed"
            )
        
        with col2:
            phone = st.text_input(
                "Phone",
                value=user.get('phone', ''),
                placeholder="+1 (555) 123-4567"
            )
            
            # Date of birth - allow dates from 1925 to Dec 31, 2025
            dob_value = None
            if user.get('date_of_birth'):
                try:
                    dob_value = datetime.strptime(user['date_of_birth'], "%Y-%m-%d").date()
                except:
                    pass
            
            date_of_birth = st.date_input(
                "Date of Birth",
                value=dob_value,
                min_value=date(1925, 1, 1),
                max_value=date(2025, 12, 31),
                help="Select your date of birth"
            )
        
        occupation = st.text_input(
            "Occupation",
            value=user.get('occupation', ''),
            placeholder="e.g., Software Engineer"
        )
        
        submitted = st.form_submit_button("Save Changes", use_container_width=True, type="primary")
        
        if submitted:
            updates = {
                'full_name': full_name,
                'phone': phone,
                'date_of_birth': date_of_birth.strftime("%Y-%m-%d") if date_of_birth else None,
                'occupation': occupation
            }
            
            if db.update_user_profile(user['id'], updates):
                st.success("Profile updated successfully!")
                # Update session state
                for key, value in updates.items():
                    st.session_state.user[key] = value
                st.rerun()
            else:
                st.error("Failed to update profile")

def render_financial_settings(user: dict, db: DatabaseManager):
    """Render financial settings section"""
    st.markdown("#### Financial Settings")
    
    with st.form("financial_settings_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            monthly_budget = st.number_input(
                "Monthly Budget",
                min_value=0.0,
                value=float(user.get('monthly_budget', 0.0)),
                step=100.0,
                help="Your target monthly spending limit"
            )
            
            hot_charges_threshold = st.number_input(
                "Hot Charges Alert ($)",
                min_value=0.0,
                value=float(user.get('hot_charges_threshold', 0.0)),
                step=10.0,
                help="Get notified for transactions above this amount"
            )
        
        with col2:
            currency_symbol = st.selectbox(
                "Preferred Currency",
                list(config.CURRENCIES.keys()),
                index=list(config.CURRENCIES.keys()).index(user.get('currency_symbol', 'USD')) if user.get('currency_symbol') in config.CURRENCIES else 0
            )
            
            salary_days = st.text_input(
                "Salary Days (comma-separated)",
                value=user.get('salary_days', ''),
                placeholder="e.g., 1,15",
                help="Days of the month you receive salary"
            )
        
        submitted = st.form_submit_button("Save Financial Settings", use_container_width=True, type="primary")
        
        if submitted:
            updates = {
                'monthly_budget': monthly_budget,
                'hot_charges_threshold': hot_charges_threshold,
                'currency_symbol': currency_symbol,
                'salary_days': salary_days
            }
            
            if db.update_user_profile(user['id'], updates):
                st.success("Financial settings updated!")
                for key, value in updates.items():
                    st.session_state.user[key] = value
                st.rerun()
            else:
                st.error("Failed to update settings")

def render_account_settings(user: dict, db: DatabaseManager):
    """Render account settings section"""
    st.markdown("#### Account Settings")
    
    # Account info
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Account Status**")
        if user.get('is_verified'):
            st.success("Email Verified")
        else:
            st.warning("Email Not Verified")
    
    with col2:
        st.markdown("**Member Since**")
        if user.get('created_at'):
            try:
                created_date = datetime.strptime(user['created_at'], "%Y-%m-%d %H:%M:%S")
                st.info(f"{created_date.strftime('%B %d, %Y')}")
            except:
                st.info("N/A")
    
    st.markdown("---")
    
    # Delete Account section
    st.markdown(" ")
    
    st.markdown("""
    <div style="
        background: rgba(255, 100, 100, 0.1);
        border: 1px solid rgba(255, 100, 100, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin-top: 16px;
    ">
        <h5 style="color: #ff6b6b; margin: 0 0 12px 0;">Delete Account</h5>
        <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin: 0;">
            Once you delete your account, there is no going back. All your data will be permanently removed.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    confirm_text = st.text_input(
        "Type 'DELETE' to confirm account deletion",
        key="delete_confirm",
        placeholder="Type DELETE here"
    )
    
    if st.button("Permanently Delete My Account", type="primary", use_container_width=True):
        if confirm_text == "DELETE":
            # Here you would implement account deletion
            st.error("Account deletion is currently disabled. Please contact support.")
        else:
            st.error("Please type 'DELETE' to confirm")