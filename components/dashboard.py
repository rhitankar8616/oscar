import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_manager import DatabaseManager

def render_dashboard(user: dict, db: DatabaseManager):
    """Render dashboard page with overview"""
    
    # Welcome message
    st.markdown(f"## Welcome back, {user.get('full_name', 'User')}!")
    st.markdown(f"*Here's your financial overview for {datetime.now().strftime('%B %Y')}*")
    st.markdown("<br>", unsafe_allow_html=True)
    
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
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="padding: 20px; background: rgba(30, 45, 65, 0.5); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.05);">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <span style="color: rgba(255,255,255,0.6); font-size: 0.75rem; text-transform: uppercase;">Monthly Budget</span>
            </div>
            <h2 style="color: white; margin: 10px 0;">${monthly_budget:,.2f}</h2>
            <p style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin: 0;">Set in Profile</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="padding: 20px; background: rgba(30, 45, 65, 0.5); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.05);">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <span style="color: rgba(255,255,255,0.6); font-size: 0.75rem; text-transform: uppercase;">Spent This Month</span>
            </div>
            <h2 style="color: white; margin: 10px 0;">${total_spent:,.2f}</h2>
            <p style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin: 0;">{num_transactions} transactions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        remaining_color = "#4CAF50" if remaining >= 0 else "#F44336"
        st.markdown(f"""
        <div style="padding: 20px; background: rgba(30, 45, 65, 0.5); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.05);">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <span style="color: rgba(255,255,255,0.6); font-size: 0.75rem; text-transform: uppercase;">Remaining Budget</span>
            </div>
            <h2 style="color: {remaining_color}; margin: 10px 0;">${remaining:,.2f}</h2>
            <p style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin: 0;">
                {percentage_used:.1f}% of budget used
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="padding: 20px; background: rgba(30, 45, 65, 0.5); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.05);">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <span style="color: rgba(255,255,255,0.6); font-size: 0.75rem; text-transform: uppercase;">Status</span>
            </div>
            <h2 style="color: {status_color}; margin: 10px 0;">{status}</h2>
            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 3px; overflow: hidden;">
                <div style="background: {status_color}; height: 100%; width: {min(percentage_used, 100)}%; transition: width 0.3s;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Two column layout for Recent Expenses and Upcoming Reminders
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Recent Expenses")
        if expenses:
            # Show last 5 expenses
            for exp in expenses[:5]:
                st.markdown(f"""
                <div style="padding: 16px; margin: 8px 0; background: rgba(30, 45, 65, 0.4); border-radius: 12px; border-left: 3px solid #FF9000;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: white;">{exp['title']}</strong><br>
                            <span style="color: rgba(255,255,255,0.5); font-size: 0.85rem;">{exp['category']} • {exp['date']}</span>
                        </div>
                        <strong style="color: #FF9000; font-size: 1.2rem;">${exp['amount']:,.2f}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("View All Expenses →", key="view_all_exp", use_container_width=True):
                st.session_state.current_page = "Expenses"
                st.rerun()
        else:
            st.info("No expenses recorded yet")
            if st.button("Add Your First Expense", key="add_first_exp", use_container_width=True):
                st.session_state.current_page = "Expenses"
                st.rerun()
    
    with col2:
        st.markdown("### Upcoming Reminders")
        reminders = db.get_user_reminders(user['id'])
        
        if reminders:
            # Show next 5 reminders
            for reminder in reminders[:5]:
                # Handle different date field names
                date_val = reminder.get('due_date') or reminder.get('date')
                if isinstance(date_val, str):
                    try:
                        due_date = datetime.strptime(date_val, "%Y-%m-%d")
                    except:
                        due_date = datetime.now()
                else:
                    due_date = date_val if date_val else datetime.now()
                
                days_until = (due_date - datetime.now()).days
                
                # Color based on urgency
                if days_until <= 3:
                    color = "#F44336"
                elif days_until <= 7:
                    color = "#FF9800"
                else:
                    color = "#4CAF50"
                
                reminder_type = reminder.get('reminder_type') or reminder.get('type') or 'Reminder'
                date_str = due_date.strftime("%Y-%m-%d") if hasattr(due_date, 'strftime') else str(due_date)
                
                st.markdown(f"""
                <div style="padding: 16px; margin: 8px 0; background: rgba(30, 45, 65, 0.4); border-radius: 12px; border-left: 3px solid {color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: white;">{reminder['title']}</strong><br>
                            <span style="color: rgba(255,255,255,0.5); font-size: 0.85rem;">{reminder_type} • {date_str}</span>
                        </div>
                        <span style="color: {color}; font-size: 0.9rem;">
                            {'Today' if days_until == 0 else 'Tomorrow' if days_until == 1 else f'{days_until}d' if days_until > 0 else 'Overdue'}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("View All Reminders →", key="view_all_rem", use_container_width=True):
                st.session_state.current_page = "Dates"
                st.rerun()
        else:
            st.info("No upcoming reminders")
            if st.button("Add Reminder", key="add_first_rem", use_container_width=True):
                st.session_state.current_page = "Dates"
                st.rerun()