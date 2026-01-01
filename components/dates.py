import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager

def render_dates(user: dict, db: DatabaseManager):
    """Render dates and reminders page"""
    st.markdown("### Important Dates & Reminders")
    
    tab1, tab2, tab3 = st.tabs(["Add Reminder", "Upcoming", "All Reminders"])
    
    with tab1:
        render_add_reminder(user, db)
    
    with tab2:
        render_upcoming_reminders(user, db)
    
    with tab3:
        render_all_reminders(user, db)

def render_add_reminder(user: dict, db: DatabaseManager):
    """Render add reminder form"""
    st.markdown("#### Create New Reminder")
    
    with st.form("reminder_form", clear_on_submit=True):
        title = st.text_input("Title*", placeholder="e.g., Pay rent")
        
        # Side by side fields
        col1, col2 = st.columns(2)
        with col1:
            reminder_type = st.selectbox(
                "Type",
                ["Bill Payment", "Subscription", "EMI", "Insurance", "Tax", "Other"]
            )
            amount = st.number_input("Amount (optional)", min_value=0.0, step=100.0)
        
        with col2:
            due_date = st.date_input("Due Date*", min_value=datetime.now().date())
            notify_days_before = st.number_input("Notify days before", min_value=0, max_value=30, value=3)
        
        description = st.text_area("Description (optional)", placeholder="Add notes...", height=60)
        
        recurring = st.checkbox("Recurring reminder")
        recurrence_type = None
        if recurring:
            recurrence_type = st.selectbox("Repeat every", ["Weekly", "Monthly", "Yearly"])
        
        submit = st.form_submit_button("Add Reminder", use_container_width=True, type="primary")
        
        if submit:
            if not title:
                st.error("Please enter a title")
            else:
                reminder_data = {
                    'user_id': user['id'],
                    'title': title,
                    'type': reminder_type,
                    'due_date': due_date.strftime("%Y-%m-%d"),
                    'amount': amount if amount > 0 else None,
                    'description': description if description else None,
                    'notify_days_before': notify_days_before,
                    'recurring': recurring,
                    'recurrence_type': recurrence_type,
                    'status': 'pending'
                }
                
                if db.add_reminder(reminder_data):
                    st.success("Reminder added!")
                    st.rerun()
                else:
                    st.error("Failed to add reminder")

def render_upcoming_reminders(user: dict, db: DatabaseManager):
    """Render upcoming reminders - compact view"""
    st.markdown("#### Upcoming (Next 30 Days)")
    
    reminders = db.get_reminders(user['id'], status='pending')
    
    if not reminders:
        st.info("No upcoming reminders")
        return
    
    df = pd.DataFrame(reminders)
    df['due_date'] = pd.to_datetime(df['due_date'])
    
    today = datetime.now()
    thirty_days = today + timedelta(days=30)
    upcoming = df[(df['due_date'] >= today) & (df['due_date'] <= thirty_days)]
    upcoming = upcoming.sort_values('due_date')
    
    if upcoming.empty:
        st.info("No reminders in the next 30 days")
        return
    
    for _, reminder in upcoming.iterrows():
        days_until = (reminder['due_date'] - today).days
        
        if days_until <= 3:
            color = "#F44336"
        elif days_until <= 7:
            color = "#FF9800"
        else:
            color = "#4CAF50"
        
        days_text = "Today!" if days_until == 0 else "Tomorrow" if days_until == 1 else f"{days_until}d"
        reminder_type = reminder.get('type') or reminder.get('reminder_type') or 'Reminder'
        
        # Main content and action buttons in same row
        col_main, col_actions = st.columns([5, 2])
        
        with col_main:
            amount_text = f" • ${reminder['amount']:,.0f}" if pd.notna(reminder.get('amount')) and reminder['amount'] > 0 else ""
            st.markdown(f"""
            <div style="border-left: 3px solid {color}; padding: 8px 10px; background: rgba(30, 45, 65, 0.5); border-radius: 6px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 1; min-width: 0;">
                        <p style="color: #ffffff; font-size: 0.82rem; font-weight: 500; margin: 0;">{reminder['title']}</p>
                        <p style="color: rgba(255,255,255,0.4); font-size: 0.6rem; margin: 0;">{reminder_type}{amount_text}</p>
                    </div>
                    <div style="text-align: right;">
                        <p style="color: {color}; font-size: 0.75rem; font-weight: 600; margin: 0;">{days_text}</p>
                        <p style="color: rgba(255,255,255,0.4); font-size: 0.55rem; margin: 0;">{reminder['due_date'].strftime('%b %d')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_actions:
            # Action buttons side by side
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("✓", key=f"done_{reminder['id']}", help="Done"):
                    db.update_reminder_status(reminder['id'], 'completed')
                    st.rerun()
            with btn_col2:
                if st.button("🗑", key=f"del_up_{reminder['id']}", help="Delete"):
                    db.delete_reminder(reminder['id'])
                    st.rerun()
        
        st.markdown('<div style="height: 2px;"></div>', unsafe_allow_html=True)

def render_all_reminders(user: dict, db: DatabaseManager):
    """Render all reminders with filters"""
    st.markdown("#### All Reminders")
    
    # Filters side by side
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Status", ["All", "Pending", "Completed", "Cancelled"], key="rem_status")
    with col2:
        type_filter = st.selectbox("Type", ["All", "Bill Payment", "Subscription", "EMI", "Insurance", "Tax", "Other"], key="rem_type")
    
    if status_filter == "All":
        reminders = db.get_all_reminders(user['id'])
    else:
        reminders = db.get_reminders(user['id'], status=status_filter.lower())
    
    if not reminders:
        st.info("No reminders found")
        return
    
    df = pd.DataFrame(reminders)
    df['due_date'] = pd.to_datetime(df['due_date'])
    
    if type_filter != "All":
        type_col = 'type' if 'type' in df.columns else 'reminder_type'
        if type_col in df.columns:
            df = df[df[type_col] == type_filter]
    
    if df.empty:
        st.info("No reminders with selected filters")
        return
    
    df = df.sort_values('due_date', ascending=False)
    
    for _, reminder in df.iterrows():
        display_reminder_card(reminder, db)

def display_reminder_card(reminder, db):
    """Display a single reminder card - compact with side by side actions"""
    reminder_type = reminder.get('type') or reminder.get('reminder_type') or 'Reminder'
    status = reminder.get('status', 'pending').capitalize()
    
    status_colors = {'Pending': '#FF9800', 'Completed': '#4CAF50', 'Cancelled': '#9E9E9E'}
    status_color = status_colors.get(status, '#FF9800')
    
    due_date_str = reminder['due_date'].strftime('%b %d, %Y')
    amount_text = f"${reminder['amount']:,.0f}" if pd.notna(reminder.get('amount')) and reminder['amount'] > 0 else ""
    
    # Main content and actions
    col_main, col_actions = st.columns([5, 2])
    
    with col_main:
        st.markdown(f"""
        <div style="background: rgba(30, 45, 65, 0.5); border-radius: 6px; padding: 8px 10px; border-left: 3px solid {status_color};">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="flex: 1; min-width: 0;">
                    <p style="color: #ffffff; font-size: 0.82rem; font-weight: 500; margin: 0;">{reminder['title']}</p>
                    <p style="color: rgba(255,255,255,0.4); font-size: 0.6rem; margin: 2px 0 0 0;">{reminder_type} • {due_date_str}</p>
                    <p style="color: {status_color}; font-size: 0.6rem; font-weight: 500; margin: 2px 0 0 0;">{status} {amount_text}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_actions:
        # All action buttons side by side
        btn_cols = st.columns(3)
        
        with btn_cols[0]:
            if reminder.get('status') == 'pending':
                if st.button("✓", key=f"comp_{reminder['id']}", help="Complete"):
                    db.update_reminder_status(reminder['id'], 'completed')
                    st.rerun()
        
        with btn_cols[1]:
            if reminder.get('status') != 'cancelled':
                if st.button("✕", key=f"canc_{reminder['id']}", help="Cancel"):
                    db.update_reminder_status(reminder['id'], 'cancelled')
                    st.rerun()
        
        with btn_cols[2]:
            if st.button("🗑", key=f"del_all_{reminder['id']}", help="Delete"):
                db.delete_reminder(reminder['id'])
                st.rerun()
    
    st.markdown('<div style="height: 2px;"></div>', unsafe_allow_html=True)