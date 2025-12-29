"""Profile settings component."""
import streamlit as st
from datetime import datetime
from database.db_manager import DatabaseManager
from utils.validators import validate_amount, validate_phone, sanitize_input
import config

def render_profile(user: dict, db: DatabaseManager):
    """Render profile settings page."""
    
    st.markdown("#### Profile")
    st.caption("Manage your personal information and preferences")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Personal Information", "Financial Settings"])
    
    with tab1:
        st.markdown("### Personal Information")
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("personal_info_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Full Name", value=user.get('full_name', ''))
                phone = st.text_input("Phone Number", value=user.get('phone', '') or '',
                                     placeholder="+1 234 567 8900")
            
            with col2:
                email = st.text_input("Email", value=user.get('email', ''), disabled=True,
                                     help="Email cannot be changed")
                dob_value = None
                if user.get('date_of_birth'):
                    try:
                        dob_value = datetime.strptime(user['date_of_birth'], "%Y-%m-%d")
                    except:
                        dob_value = None
                
                dob = st.date_input("Date of Birth", value=dob_value)
            
            occupation = st.text_input("Occupation", value=user.get('occupation', '') or '',
                                      placeholder="Software Engineer, Doctor, etc.")
            
            submitted = st.form_submit_button("Save Changes", use_container_width=True, type="primary")
            
            if submitted:
                validated_phone = None
                if phone:
                    is_valid, validated_phone, msg = validate_phone(phone)
                    if not is_valid:
                        st.error(msg)
                    else:
                        updates = {
                            'full_name': sanitize_input(full_name),
                            'phone': validated_phone if validated_phone else None,
                            'date_of_birth': dob.strftime("%Y-%m-%d") if dob else None,
                            'occupation': sanitize_input(occupation) if occupation else None
                        }
                        
                        if db.update_user_profile(user['id'], updates):
                            st.success("Profile updated successfully!")
                            st.session_state.user = db.get_user_by_email(user['email'])
                            st.rerun()
                        else:
                            st.error("Failed to update profile")
                else:
                    # No phone number provided (optional)
                    updates = {
                        'full_name': sanitize_input(full_name),
                        'phone': None,
                        'date_of_birth': dob.strftime("%Y-%m-%d") if dob else None,
                        'occupation': sanitize_input(occupation) if occupation else None
                    }
                    
                    if db.update_user_profile(user['id'], updates):
                        st.success("Profile updated successfully!")
                        st.session_state.user = db.get_user_by_email(user['email'])
                        st.rerun()
                    else:
                        st.error("Failed to update profile")
    
    with tab2:
        st.markdown("### Financial Settings")
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("financial_settings_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                monthly_budget = st.text_input("Monthly Budget ($)", 
                                              value=str(user.get('monthly_budget', 0) if user.get('monthly_budget') else 0),
                                              placeholder="Your spending limit each month")
                
                hot_charges = st.text_input("Hot Charges Threshold ($)",
                                           value=str(user.get('hot_charges_threshold', 0) if user.get('hot_charges_threshold') else 0),
                                           placeholder="Expenses above this amount are highlighted",
                                           help="Expenses above this amount are highlighted")
            
            with col2:
                currency = st.selectbox("Currency Symbol", 
                                       list(config.CURRENCIES.keys()),
                                       index=0)
                
                st.markdown("### Salary Days")
                st.caption("Days of month when you receive salary")
            
            salary_days_input = st.text_input("Salary Days (comma-separated)", 
                                             value=user.get('salary_days', '') or '',
                                             placeholder="e.g., 12, 28",
                                             help="Enter day numbers separated by commas")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button("Save Financial Settings", use_container_width=True, type="primary")
            
            if submitted:
                # Validate budget
                if not monthly_budget or monthly_budget.strip() == "":
                    monthly_budget = "0"
                
                is_valid_budget, budget_float, error_msg = validate_amount(monthly_budget)
                if not is_valid_budget:
                    st.error(f"Invalid monthly budget: {error_msg}")
                else:
                    # Validate hot charges threshold
                    if not hot_charges or hot_charges.strip() == "":
                        hot_charges = "0"
                    
                    is_valid_threshold, threshold_float, error_msg = validate_amount(hot_charges)
                    if not is_valid_threshold:
                        st.error(f"Invalid hot charges threshold: {error_msg}")
                    else:
                        salary_days = sanitize_input(salary_days_input) if salary_days_input else ''
                        
                        updates = {
                            'monthly_budget': budget_float,
                            'hot_charges_threshold': threshold_float,
                            'currency_symbol': config.CURRENCIES[currency],
                            'salary_days': salary_days
                        }
                        
                        if db.update_user_profile(user['id'], updates):
                            st.success("✅ Financial settings updated successfully!")
                            st.session_state.user = db.get_user_by_email(user['email'])
                            st.rerun()
                        else:
                            st.error("Failed to update settings")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.button("🚪 Logout", key="profile_logout", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.rerun()