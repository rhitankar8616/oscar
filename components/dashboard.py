import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager

def render_dashboard(user: dict, db: DatabaseManager):
    """Render dashboard page"""
    full_name = user.get('full_name', 'User')
    st.markdown(f"### Welcome, {full_name}!")
    
    # Get current month stats
    current_month = datetime.now().strftime("%Y-%m")
    stats = db.get_expense_stats(user['id'], month=current_month)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("This Month", f"${stats.get('total_spent', 0):,.2f}")
    
    with col2:
        st.metric("Transactions", stats.get('total_count', 0))
    
    with col3:
        avg = stats.get('avg_expense', 0) or 0
        st.metric("Avg Expense", f"${avg:,.2f}")
    
    with col4:
        budget = user.get('monthly_budget', 0) or 0
        spent = stats.get('total_spent', 0) or 0
        remaining = max(0, budget - spent)
        st.metric("Budget Left", f"${remaining:,.2f}")
    
    st.markdown("---")
    
    # Two columns for recent expenses and reminders
    col1, col2 = st.columns(2)
    
    with col1:
        render_recent_expenses(user, db)
    
    with col2:
        render_upcoming_reminders(user, db)

def render_recent_expenses(user: dict, db: DatabaseManager):
    """Render recent expenses section"""
    st.markdown("#### Recent Expenses")
    
    expenses = db.get_user_expenses(user['id'], limit=5)
    
    if not expenses:
        st.info("No expenses yet")
        if st.button("Add Expense", key="add_expense_dash"):
            st.session_state.current_page = "Expenses"
            st.rerun()
        return
    
    for expense in expenses[:5]:
        try:
            exp_date = datetime.strptime(expense['date'], "%Y-%m-%d").strftime("%b %d")
        except:
            exp_date = expense['date']
        
        st.markdown(f"""
        <div style="
            background: rgba(30, 45, 65, 0.4);
            border-radius: 8px;
            padding: 10px 12px;
            margin-bottom: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <div>
                <p style="color: #ffffff; font-size: 0.85rem; font-weight: 500; margin: 0;">{expense['title']}</p>
                <p style="color: rgba(255,255,255,0.5); font-size: 0.7rem; margin: 0;">{expense['category']}</p>
            </div>
            <div style="text-align: right;">
                <p style="color: #FF9000; font-size: 0.9rem; font-weight: 600; margin: 0;">${expense['amount']:,.2f}</p>
                <p style="color: rgba(255,255,255,0.4); font-size: 0.65rem; margin: 0;">{exp_date}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("View All Expenses", key="view_all_expenses", use_container_width=True):
        st.session_state.current_page = "Expenses"
        st.rerun()

def render_upcoming_reminders(user: dict, db: DatabaseManager):
    """Render upcoming reminders section"""
    st.markdown("#### Upcoming Reminders")
    
    reminders = db.get_user_reminders(user['id'])
    
    if not reminders:
        st.info("No upcoming reminders")
        if st.button("Add Reminder", key="add_reminder_dash"):
            st.session_state.current_page = "Dates"
            st.rerun()
        return
    
    # Sort by due date and take first 5
    df = pd.DataFrame(reminders)
    df['due_date'] = pd.to_datetime(df['due_date'])
    df = df.sort_values('due_date').head(5)
    
    today = datetime.now()
    
    for _, reminder in df.iterrows():
        days_until = (reminder['due_date'] - today).days
        
        if days_until <= 3:
            color = "#F44336"
        elif days_until <= 7:
            color = "#FF9800"
        else:
            color = "#4CAF50"
        
        if days_until == 0:
            days_text = "Today"
        elif days_until == 1:
            days_text = "Tomorrow"
        elif days_until < 0:
            days_text = "Overdue"
            color = "#F44336"
        else:
            days_text = f"{days_until}d"
        
        # Handle both field names
        due_date_val = reminder.get('due_date') or reminder.get('date')
        if hasattr(due_date_val, 'strftime'):
            due_str = due_date_val.strftime('%b %d')
        else:
            due_str = str(due_date_val)[:10]
        
        st.markdown(f"""
        <div style="
            background: rgba(30, 45, 65, 0.4);
            border-left: 3px solid {color};
            border-radius: 8px;
            padding: 10px 12px;
            margin-bottom: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <div>
                <p style="color: #ffffff; font-size: 0.85rem; font-weight: 500; margin: 0;">{reminder['title']}</p>
                <p style="color: rgba(255,255,255,0.5); font-size: 0.7rem; margin: 0;">{due_str}</p>
            </div>
            <div style="text-align: right;">
                <p style="color: {color}; font-size: 0.8rem; font-weight: 600; margin: 0;">{days_text}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("View All Reminders", key="view_all_reminders", use_container_width=True):
        st.session_state.current_page = "Dates"
        st.rerun()