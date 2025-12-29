"""Dashboard component."""
import streamlit as st
from datetime import datetime
from database.db_manager import DatabaseManager
from utils.formatters import format_currency, format_date

def render_dashboard(user: dict, db: DatabaseManager):
    """Render the main dashboard."""
    
    current_month = datetime.now().strftime("%Y-%m")
    currency = user.get('currency_symbol', '$')
    monthly_budget = user.get('monthly_budget', 0)
    
    expenses = db.get_user_expenses(user['id'], month=current_month)
    total_spent = sum(exp['amount'] for exp in expenses)
    remaining = monthly_budget - total_spent
    percentage_used = (total_spent / monthly_budget * 100) if monthly_budget > 0 else 0
    
    if percentage_used <= 50:
        status = "Excellent"
        status_color = "#4CAF50"
    elif percentage_used <= 80:
        status = "Good"
        status_color = "#FFC107"
    else:
        status = "Over Budget"
        status_color = "#F44336"
    
    st.markdown(f"## Welcome back, {user['full_name'].split()[0]}!")
    st.caption(f"Here's your financial overview for {datetime.now().strftime('%B %Y')}")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background-color: #2C3E50; padding: 20px; border-radius: 10px;'>
            <p style='color: #888; font-size: 14px; margin: 0;'>Monthly Budget</p>
            <h2 style='color: white; margin: 10px 0;'>{format_currency(monthly_budget, 'USD')}</h2>
            <p style='color: #FF9800; font-size: 14px; margin: 0; cursor: pointer;'>Update budget →</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background-color: #2C3E50; padding: 20px; border-radius: 10px;'>
            <p style='color: #888; font-size: 14px; margin: 0;'>Spent this month</p>
            <h2 style='color: white; margin: 10px 0;'>{format_currency(total_spent, 'USD')}</h2>
            <p style='color: #888; font-size: 14px; margin: 0;'>{len(expenses)} transactions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        remaining_color = "#4CAF50" if remaining >= 0 else "#F44336"
        st.markdown(f"""
        <div style='background-color: #2C3E50; padding: 20px; border-radius: 10px;'>
            <p style='color: #888; font-size: 14px; margin: 0;'>Remaining Budget</p>
            <h2 style='color: {remaining_color}; margin: 10px 0;'>{format_currency(abs(remaining), 'USD')}</h2>
            <p style='color: #888; font-size: 14px; margin: 0;'>{percentage_used:.1f}% of budget used</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background-color: #2C3E50; padding: 20px; border-radius: 10px;'>
            <p style='color: #888; font-size: 14px; margin: 0;'>Status</p>
            <h2 style='color: {status_color}; margin: 10px 0;'>{status}</h2>
            <div style='background-color: #1E2A38; height: 8px; border-radius: 4px; margin-top: 10px;'>
                <div style='background-color: {status_color}; height: 8px; border-radius: 4px; width: {min(percentage_used, 100)}%;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("### Recent Expenses")
        
        if expenses:
            for expense in expenses[:5]:
                with st.container():
                    exp_col1, exp_col2 = st.columns([3, 1])
                    with exp_col1:
                        st.markdown(f"**{expense['title']}**")
                        st.caption(f"{expense['category']} • {format_date(expense['date'])}")
                    with exp_col2:
                        st.markdown(f"**{format_currency(expense['amount'], 'USD')}**")
                    st.markdown("---")
            
            if st.button("View All", key="view_all_expenses"):
                st.session_state.current_page = "Expenses"
                st.rerun()
        else:
            st.info("No expenses yet. Start tracking your spending!")
            if st.button("Add First Expense", use_container_width=True):
                st.session_state.current_page = "Expenses"
                st.rerun()
    
    with col_right:
        st.markdown("### Upcoming")
        
        reminders = db.get_user_reminders(user['id'])
        
        if reminders:
            for reminder in reminders[:3]:
                st.markdown(f"""
                <div style='background-color: #2C3E50; padding: 15px; border-radius: 8px; margin-bottom: 10px;'>
                    <p style='color: white; margin: 0; font-weight: bold;'>{reminder['title']}</p>
                    <p style='color: #888; font-size: 12px; margin: 5px 0 0 0;'>{reminder['reminder_type']} • {format_date(reminder['date'])}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No upcoming reminders")
        
        if st.button("Add Reminder", use_container_width=True):
            st.session_state.current_page = "Dates"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### Quick Actions")
    st.caption("Manage your finances efficiently")
    
    action_col1, action_col2 = st.columns(2)
    
    with action_col1:
        if st.button("Add Expense", use_container_width=True, type="primary"):
            st.session_state.current_page = "Expenses"
            st.rerun()
    
    with action_col2:
        if st.button("View Budget Tracker", use_container_width=True):
            st.session_state.current_page = "Budget Tracker"
            st.rerun()