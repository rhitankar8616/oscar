import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_manager import DatabaseManager

def render_dashboard(user: dict, db: DatabaseManager):
    """Render dashboard page with overview"""
    
    # Welcome message
    st.markdown(f"## Welcome, {user.get('full_name', 'User')}!")
    
    # Get user data
    monthly_budget = user.get('monthly_budget', 0) or 0
    current_month = datetime.now().strftime("%Y-%m")
    expenses = db.get_user_expenses(user['id'], month=current_month)
    
    # Calculate stats
    total_spent = sum(exp['amount'] for exp in expenses) if expenses else 0
    remaining = monthly_budget - total_spent
    num_transactions = len(expenses)
    
    # Status determination
    if monthly_budget > 0:
        percentage_used = (total_spent / monthly_budget) * 100
        if percentage_used < 50:
            status = "Excellent"
            status_color = "#4CAF50"
        elif percentage_used < 80:
            status = "Good"
            status_color = "#FF9800"
        else:
            status = "Warning"
            status_color = "#F44336"
    else:
        status = "Not Set"
        status_color = "#757575"
        percentage_used = 0
    
    remaining_color = "#4CAF50" if remaining >= 0 else "#F44336"
    
    # Metrics in 2x2 grid (works on mobile too)
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    
    with row1_col1:
        st.markdown(f"""
        <div style="padding: 12px; background: rgba(30, 45, 65, 0.5); border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 8px;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.65rem; text-transform: uppercase; margin: 0 0 4px 0;">Monthly Budget</p>
            <p style="color: white; font-size: 1.1rem; font-weight: 700; margin: 0;">${monthly_budget:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with row1_col2:
        st.markdown(f"""
        <div style="padding: 12px; background: rgba(30, 45, 65, 0.5); border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 8px;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.65rem; text-transform: uppercase; margin: 0 0 4px 0;">Spent This Month</p>
            <p style="color: white; font-size: 1.1rem; font-weight: 700; margin: 0;">${total_spent:,.2f}</p>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.6rem; margin: 2px 0 0 0;">{num_transactions} transactions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with row2_col1:
        st.markdown(f"""
        <div style="padding: 12px; background: rgba(30, 45, 65, 0.5); border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 8px;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.65rem; text-transform: uppercase; margin: 0 0 4px 0;">Remaining</p>
            <p style="color: {remaining_color}; font-size: 1.1rem; font-weight: 700; margin: 0;">${remaining:,.2f}</p>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.6rem; margin: 2px 0 0 0;">{percentage_used:.0f}% used</p>
        </div>
        """, unsafe_allow_html=True)
    
    with row2_col2:
        st.markdown(f"""
        <div style="padding: 12px; background: rgba(30, 45, 65, 0.5); border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 8px;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.65rem; text-transform: uppercase; margin: 0 0 4px 0;">Status</p>
            <p style="color: {status_color}; font-size: 1.1rem; font-weight: 700; margin: 0;">{status}</p>
            <div style="background: rgba(255,255,255,0.1); height: 4px; border-radius: 2px; margin-top: 4px;">
                <div style="background: {status_color}; height: 100%; width: {min(percentage_used, 100)}%; border-radius: 2px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent Expenses and Upcoming Reminders side by side
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Recent Expenses")
        if expenses:
            for exp in expenses[:4]:
                st.markdown(f"""
                <div style="padding: 8px 10px; margin: 4px 0; background: rgba(30, 45, 65, 0.4); border-radius: 8px; border-left: 2px solid #FF9000;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1; min-width: 0;">
                            <p style="color: white; font-size: 0.8rem; font-weight: 500; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{exp['title']}</p>
                            <p style="color: rgba(255,255,255,0.4); font-size: 0.65rem; margin: 0;">{exp['category']}</p>
                        </div>
                        <p style="color: #FF9000; font-size: 0.85rem; font-weight: 600; margin: 0 0 0 8px;">${exp['amount']:,.2f}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("View All →", key="view_exp", use_container_width=True):
                st.session_state.current_page = "Expenses"
                st.rerun()
        else:
            st.info("No expenses yet")
    
    with col2:
        st.markdown("#### Upcoming Reminders")
        reminders = db.get_user_reminders(user['id'])
        
        if reminders:
            for reminder in reminders[:4]:
                date_val = reminder.get('due_date') or reminder.get('date')
                if isinstance(date_val, str):
                    try:
                        due_date = datetime.strptime(date_val, "%Y-%m-%d")
                    except:
                        due_date = datetime.now()
                else:
                    due_date = date_val if date_val else datetime.now()
                
                days_until = (due_date - datetime.now()).days
                color = "#F44336" if days_until <= 3 else "#FF9800" if days_until <= 7 else "#4CAF50"
                days_text = "Today" if days_until == 0 else f"{days_until}d"
                
                st.markdown(f"""
                <div style="padding: 8px 10px; margin: 4px 0; background: rgba(30, 45, 65, 0.4); border-radius: 8px; border-left: 2px solid {color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1; min-width: 0;">
                            <p style="color: white; font-size: 0.8rem; font-weight: 500; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{reminder['title']}</p>
                            <p style="color: rgba(255,255,255,0.4); font-size: 0.65rem; margin: 0;">{due_date.strftime('%b %d')}</p>
                        </div>
                        <p style="color: {color}; font-size: 0.75rem; font-weight: 600; margin: 0 0 0 8px;">{days_text}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("View All →", key="view_rem", use_container_width=True):
                st.session_state.current_page = "Dates"
                st.rerun()
        else:
            st.info("No reminders")